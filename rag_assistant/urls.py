from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    KnowledgeDocumentViewSet,
    ChatViewSet,
    AlexiaViewSet,
    CloudFunctionWebhookView
)

router = DefaultRouter()
router.register(r'knowledge/documents', KnowledgeDocumentViewSet, basename='knowledge-documents')
router.register(r'chat', ChatViewSet, basename='chat')
router.register(r'alexia', AlexiaViewSet, basename='alexia')

urlpatterns = [
    # Webhook serverless para Cloud Functions futuras
    path(
        'knowledge/webhook/document-extracted/',
        CloudFunctionWebhookView.as_view(),
        name='cloud-function-webhook'
    ),
    # Atajo de búsqueda vectorial
    path(
        'knowledge/test-search/',
        KnowledgeDocumentViewSet.as_view({'post': 'test_search'}),
        name='knowledge-test-search'
    ),
    # Rutas generadas por DefaultRouter
    path('', include(router.urls)),
]
