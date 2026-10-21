from django.contrib import admin
from django.utils.html import format_html
from .models import KnowledgeDocument, KnowledgeChunk, ChatSession, ChatMessage


class KnowledgeChunkInline(admin.TabularInline):
    model = KnowledgeChunk
    extra = 0
    can_delete = False
    fields = ('chunk_index', 'token_count', 'content_snippet', 'has_embedding', 'created_at')
    readonly_fields = ('chunk_index', 'token_count', 'content_snippet', 'has_embedding', 'created_at')

    def content_snippet(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_snippet.short_description = "Contenido"

    def has_embedding(self, obj):
        return bool(obj.embedding and len(obj.embedding) > 0)
    has_embedding.boolean = True
    has_embedding.short_description = "Embedding"


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'document_type',
        'ingestion_source',
        'status_badge',
        'chunks_count',
        'file_size_display',
        'uploaded_by',
        'created_at'
    )
    list_filter = ('status', 'document_type', 'ingestion_source', 'created_at')
    search_fields = ('title', 'description', 'storage_path')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('chunks_count', 'created_at', 'updated_at')
    inlines = [KnowledgeChunkInline]
    fieldsets = (
        ('Identificación', {
            'fields': ('title', 'slug', 'description', 'document_type')
        }),
        ('Almacenamiento Firebase & Archivo', {
            'fields': ('ingestion_source', 'file_url', 'storage_path', 'file_size_bytes', 'file')
        }),
        ('Estado de Indexación RAG', {
            'fields': ('status', 'chunks_count', 'error_message', 'raw_text')
        }),
        ('Metadatos y Auditoría', {
            'fields': ('uploaded_by', 'created_at', 'updated_at')
        }),
    )

    def file_size_display(self, obj):
        if not obj.file_size_bytes:
            return "0 KB"
        kb = obj.file_size_bytes / 1024
        if kb > 1024:
            return f"{kb / 1024:.2f} MB"
        return f"{kb:.1f} KB"
    file_size_display.short_description = "Tamaño"

    def status_badge(self, obj):
        colors = {
            'INDEXED': '#28a745',
            'PENDING': '#ffc107',
            'EXTRACTING': '#17a2b8',
            'FAILED': '#dc3545',
            'ARCHIVED': '#6c757d',
        }
        color = colors.get(obj.status, '#333')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Estado"


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'token_count', 'has_embedding', 'created_at')
    list_filter = ('document__document_type', 'created_at')
    search_fields = ('content', 'document__title')
    readonly_fields = ('created_at',)

    def has_embedding(self, obj):
        return bool(obj.embedding and len(obj.embedding) > 0)
    has_embedding.boolean = True
    has_embedding.short_description = "Tiene Embedding"


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    can_delete = False
    fields = ('role', 'content_snippet', 'is_crisis_detected', 'created_at')
    readonly_fields = ('role', 'content_snippet', 'is_crisis_detected', 'created_at')

    def content_snippet(self, obj):
        return obj.content[:120] + '...' if len(obj.content) > 120 else obj.content
    content_snippet.short_description = "Mensaje"


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'channel', 'user', 'is_anonymous', 'messages_count', 'created_at', 'updated_at')
    list_filter = ('channel', 'is_anonymous', 'created_at')
    search_fields = ('session_id', 'user__username', 'user__email')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    inlines = [ChatMessageInline]

    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = "Mensajes"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'crisis_badge', 'content_snippet', 'created_at')
    list_filter = ('role', 'is_crisis_detected', 'created_at')
    search_fields = ('content', 'session__session_id')
    readonly_fields = ('created_at',)

    def content_snippet(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_snippet.short_description = "Contenido"

    def crisis_badge(self, obj):
        if obj.is_crisis_detected:
            return format_html('<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">CRISIS</span>')
        return format_html('<span style="color: #6c757d;">No</span>')
    crisis_badge.short_description = "Alerta Crisis"
