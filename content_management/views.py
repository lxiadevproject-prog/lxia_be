from django.db.models import F
from django.utils import timezone
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from authentication.permissions import IsContentManager
from .models import Category, Tag, Article, Resource
from .permissions import IsContentManagerOrReadOnly
from .serializers import (
    CategorySerializer,
    TagSerializer,
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleWriteSerializer,
    ResourceSerializer,
)


@extend_schema(tags=["Portal y CMS - Categorías"])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD de categorías temáticas para organizar guías y artículos.
    Lectura pública; creación y edición restringidas a Administradores de Contenido y Superadmin.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsContentManagerOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']

    def get_queryset(self):
        user = self.request.user
        # Usuarios no administrativos solo ven categorías activas
        if not user.is_authenticated or not (user.is_superuser or getattr(user, 'profile', None) and (user.profile.is_content_manager or user.profile.is_superadmin)):
            return Category.objects.filter(is_active=True)
        return Category.objects.all()


@extend_schema(tags=["Portal y CMS - Etiquetas"])
class TagViewSet(viewsets.ModelViewSet):
    """
    CRUD de etiquetas para clasificación temática y filtros cruzados.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsContentManagerOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema(tags=["Portal Web - Contenidos Públicos"])
class PublicArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints públicos de solo lectura para el portal web de autocuidado (RF-CNT-01).
    Solo entrega artículos en estado 'PUBLICADO'.
    Optimizados para bajo consumo de datos móviles (RF-CNT-04).
    """
    queryset = Article.objects.filter(status=Article.Status.PUBLISHED).select_related('category', 'author').prefetch_related('tags')
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'tags__slug']
    search_fields = ['title', 'summary', 'body']
    ordering_fields = ['published_at', 'views_count', 'title']
    ordering = ['-published_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrementar contador de lecturas de forma atómica y segura
        Article.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db(fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema(tags=["CMS - Gestión de Contenidos (Admin)"])
class ManageArticleViewSet(viewsets.ModelViewSet):
    """
    Panel administrativo CMS para Administradores de Contenido y Superadmin (RF-CNT-03).
    Permite gestionar borradores, publicar, archivar y actualizar artículos.
    """
    queryset = Article.objects.all().select_related('category', 'author').prefetch_related('tags')
    permission_classes = [IsContentManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'category__slug', 'tags__slug']
    search_fields = ['title', 'summary', 'body']
    ordering_fields = ['published_at', 'created_at', 'views_count', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleWriteSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article = serializer.save()
        read_serializer = ArticleDetailSerializer(article, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        article = serializer.save()
        read_serializer = ArticleDetailSerializer(article, context={'request': request})
        return Response(read_serializer.data)

    @extend_schema(
        responses={200: ArticleDetailSerializer},
        description="Publica inmediatamente el artículo y asigna la fecha de publicación actual."
    )
    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        article = self.get_object()
        article.status = Article.Status.PUBLISHED
        article.published_at = timezone.now()
        article.save()
        return Response(
            ArticleDetailSerializer(article, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        responses={200: ArticleDetailSerializer},
        description="Archiva el artículo retirándolo de la vista pública sin eliminarlo de la base de datos."
    )
    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        article = self.get_object()
        article.status = Article.Status.ARCHIVED
        article.save()
        return Response(
            ArticleDetailSerializer(article, context={'request': request}).data,
            status=status.HTTP_200_OK
        )


@extend_schema(tags=["Portal y CMS - Recursos y Descargables"])
class ResourceViewSet(viewsets.ModelViewSet):
    """
    Gestión y entrega de recursos descargables (PDFs, guías, enlaces externos).
    Lectura y descarga pública; gestión restringida a Administradores de Contenido.
    """
    queryset = Resource.objects.all().select_related('category')
    serializer_class = ResourceSerializer
    permission_classes = [IsContentManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'is_featured', 'category', 'category__slug']
    search_fields = ['title', 'description']
    ordering_fields = ['download_count', 'created_at']
    ordering = ['-is_featured', '-created_at']

    @extend_schema(
        responses={200: OpenApiResponse(description="Contador de descargas incrementado exitosamente")},
        description="Registra la descarga o acceso a un recurso de apoyo."
    )
    @action(detail=True, methods=['post'], permission_classes=[AllowAny], url_path='track-download')
    def track_download(self, request, pk=None):
        resource = self.get_object()
        Resource.objects.filter(pk=resource.pk).update(download_count=F('download_count') + 1)
        resource.refresh_from_db(fields=['download_count'])
        return Response({
            'detail': 'Descarga registrada correctamente.',
            'download_count': resource.download_count
        }, status=status.HTTP_200_OK)
