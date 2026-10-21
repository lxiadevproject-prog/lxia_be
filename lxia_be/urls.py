"""
URL configuration for lxia_be project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Router principal de Django REST Framework
router = DefaultRouter()
# Registrar ViewSets aquí:
# router.register(r'users', UserViewSet)

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # Documentación OpenAPI 3 / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Módulo de Autenticación y Usuarios
    path('api/v1/auth/', include('authentication.urls')),

    # Módulo de Gestión y Entrega de Contenidos (CMS / Portal Web)
    path('api/v1/content/', include('content_management.urls')),

    # Módulo de Asistente Conversacional & RAG (Alexia)
    path('api/v1/', include('rag_assistant.urls')),

    # Endpoints de la API
    path('api/v1/', include(router.urls)),
]

# Servir archivos multimedia en desarrollo local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
