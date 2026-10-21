import logging
from typing import List, Tuple

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from authentication.permissions import IsResearcher
from .models import KnowledgeDocument, KnowledgeChunk, ChatSession, ChatMessage
from .serializers import (
    KnowledgeDocumentListSerializer,
    KnowledgeDocumentDetailSerializer,
    KnowledgeDocumentCreateSerializer,
    TestSearchRequestSerializer,
    ChatMessageInputSerializer,
    ChatMessageOutputSerializer,
    ChatSessionHistorySerializer,
    CloudFunctionWebhookSerializer,
)
from .services.orchestrator import RAGOrchestrator
from .services.ingestion import DocumentIngestionService
from .services.vector_search import search_similar_chunks

logger = logging.getLogger(__name__)


# ============================================================================
# ENDPOINTS DE BASE DE CONOCIMIENTO (INVESTIGACIÓN / SUPERADMIN)
# ============================================================================

@extend_schema(tags=["RAG - Base de Conocimiento"])
class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    """
    Gestión integral de documentos y fuentes de conocimiento para el motor RAG.
    Admite registro ligero mediante URLs directas de Firebase Storage (0 MB de ancho de banda en Render).
    Acceso restringido a miembros del Equipo de Investigación o Superadministradores.
    """
    queryset = KnowledgeDocument.objects.all().select_related('uploaded_by')
    permission_classes = [IsResearcher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type', 'ingestion_source']
    search_fields = ['title', 'description', 'storage_path']
    ordering_fields = ['created_at', 'chunks_count', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return KnowledgeDocumentCreateSerializer
        elif self.action == 'retrieve':
            return KnowledgeDocumentDetailSerializer
        return KnowledgeDocumentListSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(uploaded_by=user)

    @extend_schema(
        summary="Disparar indexación de documento",
        description="Inicia la extracción de texto, fragmentación y cálculo de embeddings para el documento.",
        responses={200: OpenApiResponse(description="Documento indexado exitosamente.")}
    )
    @action(detail=True, methods=['post'], url_path='index')
    def trigger_index(self, request, pk=None):
        document = self.get_object()
        service = DocumentIngestionService()
        result = service.index_document(document)
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Probar búsqueda vectorial en vivo",
        request=TestSearchRequestSerializer,
        responses={200: OpenApiResponse(description="Fragmentos recuperados con sus puntuaciones de similitud de coseno.")}
    )
    @action(detail=False, methods=['post'], url_path='test-search')
    def test_search(self, request):
        serializer = TestSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data['query']
        top_k = serializer.validated_data['top_k']
        threshold = serializer.validated_data['threshold']

        matches = search_similar_chunks(query, top_k=top_k, threshold=threshold)
        results = []
        for chunk, score in matches:
            results.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document.id,
                "document_title": chunk.document.title,
                "score": round(score, 4),
                "page": chunk.metadata.get('page', 1) if isinstance(chunk.metadata, dict) else 1,
                "content_snippet": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            })

        return Response({
            "query": query,
            "total_matches": len(results),
            "results": results
        }, status=status.HTTP_200_OK)


# ============================================================================
# ENDPOINTS PÚBLICOS DE CHAT CONVERSACIONAL Y ALEXIA AVATAR
# ============================================================================

@extend_schema(tags=["RAG - Asistente y Alexia"])
class ChatViewSet(viewsets.ViewSet):
    """
    Endpoints de interacción conversacional pública y anónima con el motor RAG de Alexia.
    Cumple con el requerimiento de privacidad RF-OBS-02.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Enviar mensaje a Alexia (RAG + Detección de Crisis)",
        request=ChatMessageInputSerializer,
        responses={200: ChatMessageOutputSerializer}
    )
    @action(detail=False, methods=['post'], url_path='message')
    def send_message(self, request):
        serializer = ChatMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        channel = serializer.validated_data.get('channel', 'PORTAL_WEB')

        session = None
        if session_id:
            session = ChatSession.objects.filter(session_id=session_id).first()

        if not session:
            session = ChatSession.objects.create(
                channel=channel,
                is_anonymous=True,
                user=request.user if request.user.is_authenticated else None
            )

        orchestrator = RAGOrchestrator()
        rag_response = orchestrator.process_query(user_message, session=session)

        response_payload = {
            "session_id": session.session_id,
            "role": "ASSISTANT",
            "content": rag_response['content'],
            "citations": rag_response.get('citations', []),
            "is_crisis_detected": rag_response.get('is_crisis', False),
            "suggested_expression": rag_response.get('suggested_expression', 'INFORMATIVE'),
            "tts_clean_text": rag_response.get('tts_clean_text', ''),
            "latency_ms": rag_response.get('latency_ms', 0),
            "emergency_hotlines": rag_response.get('emergency_hotlines', [])
        }

        output_serializer = ChatMessageOutputSerializer(data=response_payload)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Consultar historial de conversación por sesión",
        parameters=[
            OpenApiParameter("session_id", str, OpenApiParameter.PATH, description="UUID de la sesión de chat")
        ],
        responses={200: ChatSessionHistorySerializer}
    )
    @action(detail=False, methods=['get'], url_path='history/(?P<session_id>[0-9a-f-]+)')
    def get_history(self, request, session_id=None):
        session = get_object_or_404(ChatSession, session_id=session_id)
        serializer = ChatSessionHistorySerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["RAG - Asistente y Alexia"])
class AlexiaViewSet(viewsets.ViewSet):
    """
    Endpoint especializado para el Avatar Tridimensional/Interactivo de Alexia.
    Retorna metadatos optimizados para la síntesis de voz (TTS limpio sin Markdown)
    y sugerencias de expresión visual/emocional (RF-ALX-01 a 03).
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Interacción dedicada con Avatar Alexia",
        request=ChatMessageInputSerializer,
        responses={200: ChatMessageOutputSerializer}
    )
    @action(detail=False, methods=['post'], url_path='interact')
    def interact(self, request):
        serializer = ChatMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        session = None
        if session_id:
            session = ChatSession.objects.filter(session_id=session_id).first()

        if not session:
            session = ChatSession.objects.create(
                channel='ALEXIA_AVATAR',
                is_anonymous=True,
                user=request.user if request.user.is_authenticated else None
            )

        orchestrator = RAGOrchestrator()
        rag_response = orchestrator.process_query(user_message, session=session)

        response_payload = {
            "session_id": session.session_id,
            "role": "ASSISTANT",
            "content": rag_response['content'],
            "citations": rag_response.get('citations', []),
            "is_crisis_detected": rag_response.get('is_crisis', False),
            "suggested_expression": rag_response.get('suggested_expression', 'EMPATHETIC'),
            "tts_clean_text": rag_response.get('tts_clean_text', ''),
            "latency_ms": rag_response.get('latency_ms', 0),
            "emergency_hotlines": rag_response.get('emergency_hotlines', [])
        }

        output_serializer = ChatMessageOutputSerializer(data=response_payload)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# WEBHOOK SEGURO PARA FIREBASE CLOUD FUNCTIONS (PLUG-AND-PLAY SERVERLESS)
# ============================================================================

@extend_schema(tags=["RAG - Webhook Serverless"])
class CloudFunctionWebhookView(views.APIView):
    """
    Receptor seguro para la extracción de texto serverless desde Firebase Cloud Functions.
    Permite delegar la extracción pesada de PDFs a GCP sin consumir memoria en el servidor Render.
    Autenticación mediante cabecera HTTP 'X-Webhook-Secret'.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Webhook de recepción de texto extraído por Cloud Function",
        request=CloudFunctionWebhookSerializer,
        responses={
            200: OpenApiResponse(description="Texto recibido e indexado en fragmentos vectoriales."),
            403: OpenApiResponse(description="Secreto de webhook no válido."),
            404: OpenApiResponse(description="Documento no encontrado.")
        }
    )
    def post(self, request):
        # 1. Validar cabecera secreta
        secret_header = request.headers.get('X-Webhook-Secret') or request.META.get('HTTP_X_WEBHOOK_SECRET')
        expected_secret = getattr(settings, 'CLOUD_FUNCTION_WEBHOOK_SECRET', '')

        if not secret_header or secret_header != expected_secret:
            logger.warning("Intento de acceso al webhook con secreto inválido o ausente.")
            return Response(
                {"error": "Secreto de webhook inválido o no proporcionado (X-Webhook-Secret)."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Validar payload
        serializer = CloudFunctionWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        document = None

        if data.get('document_id'):
            document = KnowledgeDocument.objects.filter(id=data['document_id']).first()
        elif data.get('storage_path'):
            document = KnowledgeDocument.objects.filter(storage_path=data['storage_path']).first()
        elif data.get('file_url'):
            document = KnowledgeDocument.objects.filter(file_url=data['file_url']).first()

        if not document:
            return Response(
                {"error": "No se encontró ningún KnowledgeDocument que coincida con los identificadores provistos."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Transformar estructura de páginas si fue provista
        raw_pages: List[dict] = data.get('pages_data', [])
        pages_tuples: List[Tuple[int, str]] = []
        for p in raw_pages:
            p_num = p.get('page', 1)
            p_txt = p.get('text', '')
            if p_txt.strip():
                pages_tuples.append((int(p_num), p_txt.strip()))

        # 4. Delegar indexación en el servicio
        document.ingestion_source = 'CLOUD_FUNCTION_WEBHOOK'
        document.save(update_fields=['ingestion_source'])
        service = DocumentIngestionService()
        result = service.index_from_extracted_text(
            document=document,
            raw_text=data['extracted_text'],
            pages_data=pages_tuples if len(pages_tuples) > 0 else None
        )

        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
