from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import UserProfile
from .permissions import IsSuperadmin
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)


class LoginView(APIView):
    """
    Endpoint para inicio de sesión de usuarios administrativos e investigadores.
    Retorna el token de acceso y la información del usuario con su rol.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Inicio de sesión exitoso"),
            400: OpenApiResponse(description="Credenciales inválidas"),
        },
        description="Autentica las credenciales (username/password) y genera o retorna el token de acceso.",
        tags=["Autenticación"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.create_or_get_token()

        return Response({
            'token': token,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Endpoint para cerrar sesión e invalidar el token de autenticación del usuario.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description="Sesión cerrada correctamente")},
        description="Elimina el token de sesión del usuario autenticado.",
        tags=["Autenticación"]
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Sesión cerrada exitosamente.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    Retorna la información del usuario autenticado y su perfil de rol.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        description="Obtiene los datos del usuario actualmente autenticado.",
        tags=["Autenticación"]
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    """
    Permite al usuario autenticado cambiar su propia contraseña.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Contraseña actualizada"),
            400: OpenApiResponse(description="Error de validación"),
        },
        description="Actualiza la contraseña del usuario en sesión verificando la contraseña anterior.",
        tags=["Autenticación"]
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Contraseña actualizada exitosamente.'}, status=status.HTTP_200_OK)


@extend_schema(tags=["Gestión de Usuarios (Superadmin)"])
class UserManagementViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de usuarios administrativos (Superadmin, Investigador, Admin de Contenidos).
    Solo accesible por usuarios con rol Superadmin.
    """
    queryset = User.objects.all().select_related('profile').prefetch_related('groups').order_by('-id')
    permission_classes = [IsSuperadmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)

    def destroy(self, request, *args, **kwargs):
        user_to_delete = self.get_object()
        if user_to_delete == request.user:
            return Response(
                {'detail': 'No puedes eliminar tu propia cuenta de superadministrador.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
