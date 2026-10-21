from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Tag, Article, Resource


class CategorySerializer(serializers.ModelSerializer):
    articles_count = serializers.IntegerField(source='articles.count', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'icon',
            'order',
            'is_active',
            'articles_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Serializador ultraligero optimizado para listados y tarjetas en el portal web (RF-CNT-04).
    Omite el campo 'body' para reducir drásticamente la carga de datos en conexiones móviles.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    author_name = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'slug',
            'summary',
            'featured_image',
            'category',
            'category_name',
            'category_slug',
            'tags',
            'status',
            'status_display',
            'author_name',
            'reading_time_minutes',
            'views_count',
            'published_at',
            'created_at',
        ]
        read_only_fields = fields

    def get_author_name(self, obj):
        if not obj.author:
            return "Equipo TransLúcidas"
        name = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return name if name else obj.author.username


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Serializador completo con el cuerpo del artículo y metadatos de categoría.
    Utilizado al consultar el detalle de un artículo en particular.
    """
    category = CategorySerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    author_name = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'slug',
            'summary',
            'body',
            'featured_image',
            'category',
            'tags',
            'status',
            'status_display',
            'author_name',
            'reading_time_minutes',
            'views_count',
            'published_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_author_name(self, obj):
        if not obj.author:
            return "Equipo TransLúcidas"
        name = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return name if name else obj.author.username


class ArticleWriteSerializer(serializers.ModelSerializer):
    """
    Serializador de escritura para creación y edición de artículos en el panel administrativo CMS.
    """
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'slug',
            'summary',
            'body',
            'featured_image',
            'category',
            'tags',
            'status',
            'reading_time_minutes',
            'published_at',
        ]
        read_only_fields = ['id', 'slug', 'reading_time_minutes', 'published_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        request = self.context.get('request')
        author = request.user if request and request.user.is_authenticated else None
        
        article = Article.objects.create(author=author, **validated_data)
        if tags:
            article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class ResourceSerializer(serializers.ModelSerializer):
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Resource
        fields = [
            'id',
            'title',
            'description',
            'resource_type',
            'resource_type_display',
            'file',
            'external_url',
            'category',
            'category_name',
            'is_featured',
            'download_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'download_count', 'created_at', 'updated_at']

    def validate(self, attrs):
        file = attrs.get('file', getattr(self.instance, 'file', None))
        external_url = attrs.get('external_url', getattr(self.instance, 'external_url', None))

        if not file and not external_url:
            raise serializers.ValidationError(
                "Debes proporcionar al menos un archivo descargable o una URL externa para el recurso."
            )
        return attrs
