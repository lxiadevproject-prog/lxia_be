from rest_framework import serializers
from .models import KnowledgeDocument, KnowledgeChunk, ChatSession, ChatMessage


# ============================================================================
# SERIALIZADORES DE DOCUMENTOS Y BASE DE CONOCIMIENTO
# ============================================================================

class KnowledgeDocumentListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    ingestion_source_display = serializers.CharField(source='get_ingestion_source_display', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True, default=None)

    class Meta:
        model = KnowledgeDocument
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'document_type',
            'document_type_display',
            'ingestion_source',
            'ingestion_source_display',
            'file_url',
            'storage_path',
            'file_size_bytes',
            'status',
            'status_display',
            'chunks_count',
            'uploaded_by_username',
            'created_at',
            'updated_at'
        ]


class KnowledgeDocumentDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    ingestion_source_display = serializers.CharField(source='get_ingestion_source_display', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True, default=None)

    class Meta:
        model = KnowledgeDocument
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'document_type',
            'document_type_display',
            'ingestion_source',
            'ingestion_source_display',
            'file_url',
            'storage_path',
            'file_size_bytes',
            'status',
            'status_display',
            'chunks_count',
            'raw_text',
            'error_message',
            'uploaded_by_username',
            'created_at',
            'updated_at'
        ]


class KnowledgeDocumentCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar documentos en la base de conocimiento.
    Admite subida de URLs de Firebase Storage (0 MB de impacto en el servidor Render)
    o subida de archivo local/texto directo.
    """
    class Meta:
        model = KnowledgeDocument
        fields = [
            'id',
            'title',
            'description',
            'document_type',
            'ingestion_source',
            'file_url',
            'storage_path',
            'file_size_bytes',
            'file',
            'raw_text',
            'status',
            'chunks_count',
            'created_at'
        ]
        read_only_fields = ['status', 'chunks_count', 'created_at']

    def validate(self, attrs):
        source = attrs.get('ingestion_source', 'FIREBASE_DIRECT')
        if source == 'FIREBASE_DIRECT' and not attrs.get('file_url') and not attrs.get('storage_path'):
            raise serializers.ValidationError(
                "Para subidas directas a Firebase se requiere al menos 'file_url' o 'storage_path'."
            )
        if source == 'MANUAL_TEXT' and not attrs.get('raw_text'):
            raise serializers.ValidationError(
                "Para fuentes de texto manual o FAQ se requiere el campo 'raw_text'."
            )
        return attrs


class TestSearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, min_length=2, max_length=500)
    top_k = serializers.IntegerField(required=False, default=4, min_value=1, max_value=10)
    threshold = serializers.FloatField(required=False, default=0.15, min_value=0.0, max_value=1.0)


# ============================================================================
# SERIALIZADORES DE CHAT, ALEXIA Y AUDITORÍA
# ============================================================================

class CitationSerializer(serializers.Serializer):
    document_id = serializers.IntegerField(required=False)
    document_title = serializers.CharField()
    chunk_id = serializers.IntegerField(required=False)
    chunk_index = serializers.IntegerField(required=False)
    page = serializers.IntegerField(required=False, default=1)
    section = serializers.CharField(required=False, default='General')
    snippet = serializers.CharField()


class ChatMessageInputSerializer(serializers.Serializer):
    message = serializers.CharField(
        required=True,
        min_length=1,
        max_length=2000,
        help_text="Consulta en lenguaje natural enviada por la persona usuaria."
    )
    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="UUID de la sesión activa. Si no se envía, el servidor genera una sesión nueva."
    )
    channel = serializers.ChoiceField(
        choices=ChatSession.CHANNEL_CHOICES,
        default='PORTAL_WEB',
        required=False,
        help_text="Canal de origen (PORTAL_WEB, ALEXIA_AVATAR, MOBILE_APP, TEST_PANEL)."
    )


class ChatMessageOutputSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    role = serializers.CharField(default='ASSISTANT')
    content = serializers.CharField()
    citations = CitationSerializer(many=True, required=False, default=list)
    is_crisis_detected = serializers.BooleanField(default=False)
    suggested_expression = serializers.CharField(required=False, default='INFORMATIVE')
    tts_clean_text = serializers.CharField(required=False, default='')
    latency_ms = serializers.IntegerField(required=False, default=0)
    emergency_hotlines = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )


class ChatMessageHistoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'role',
            'content',
            'citations',
            'is_crisis_detected',
            'metadata',
            'created_at'
        ]


class ChatSessionHistorySerializer(serializers.ModelSerializer):
    messages = ChatMessageHistoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'session_id',
            'channel',
            'is_anonymous',
            'created_at',
            'updated_at',
            'messages'
        ]


# ============================================================================
# SERIALIZADOR DE WEBHOOK PARA CLOUD FUNCTIONS (FUTURE-PROOFING)
# ============================================================================

class CloudFunctionWebhookSerializer(serializers.Serializer):
    """
    Carga útil esperada desde la Firebase Cloud Function cuando extrae texto de un PDF en GCP.
    """
    storage_path = serializers.CharField(required=False, allow_blank=True)
    document_id = serializers.IntegerField(required=False, allow_null=True)
    file_url = serializers.URLField(required=False, allow_blank=True)
    extracted_text = serializers.CharField(required=True, min_length=1)
    pages_data = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
        help_text="Lista opcional de objetos [{'page': 1, 'text': '...'}]"
    )

    def validate(self, attrs):
        if not attrs.get('document_id') and not attrs.get('storage_path') and not attrs.get('file_url'):
            raise serializers.ValidationError(
                "Debe proporcionar al menos 'document_id', 'storage_path' o 'file_url' para asociar el texto al documento."
            )
        return attrs
