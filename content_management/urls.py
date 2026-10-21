from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    TagViewSet,
    PublicArticleViewSet,
    ManageArticleViewSet,
    ResourceViewSet,
)

router = DefaultRouter()

# Endpoints públicos y de consulta
router.register(r'categories', CategoryViewSet, basename='content-category')
router.register(r'tags', TagViewSet, basename='content-tag')
router.register(r'articles', PublicArticleViewSet, basename='content-article')
router.register(r'resources', ResourceViewSet, basename='content-resource')

# Panel de gestión CMS (requiere autenticación Content Manager / Superadmin)
router.register(r'manage/articles', ManageArticleViewSet, basename='manage-article')

urlpatterns = [
    path('', include(router.urls)),
]
