import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class KnowledgeDocument(models.Model):
    """
    Fuente documental registrada en la base de conocimiento de Alexia / RAG.
    Diseñado para operar con URLs de Firebase Storage (0 MB de impacto en el servidor de Render),
    archivos locales en desarrollo o integración directa vía Cloud Functions.
    """
    DOCUMENT_TYPES = (
        ('GUIDE', 'Guía de Atención Integral'),
        ('PROTOCOL', 'Protocolo Médico / Psicosocial'),
        ('LEGAL', 'Marco Legal y Derechos'),
        ('WORKSHOP', 'Taller / Material Pedagógico'),
        ('FAQ', 'Preguntas Frecuentes'),
        ('OTHER', 'Otro Documento'),
    )

    INGESTION_SOURCES = (
        ('MANUAL_TEXT', 'Texto Manual / FAQ'),
        ('FIREBASE_DIRECT', 'Subida Directa a Firebase Storage'),
        ('CLOUD_FUNCTION_WEBHOOK', 'Webhook Firebase Cloud Function (Serverless)'),
        ('LOCAL_FILE', 'Archivo Local Django'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pendiente de indexar'),
        ('EXTRACTING', 'Extrayendo texto'),
        ('INDEXED', 'Indexado y activo en RAG'),
        ('FAILED', 'Error en indexación'),
        ('ARCHIVED', 'Archivado (inactivo)'),
    )

    title = models.CharField(max_length=255, verbose_name="Título")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción o resumen")
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPES,
        default='GUIDE',
        verbose_name="Tipo de documento"
    )

    # Integración con Firebase Storage
    file_url = models.URLField(
        max_length=1000,
        blank=True,
        verbose_name="URL en Firebase Storage",
        help_text="URL pública o firmada del archivo alojado en Firebase Storage"
    )
    storage_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta en Storage Bucket",
        help_text="Ruta del objeto en el bucket (ej. knowledge_docs/guia_trans_2026.pdf)"
    )
    file_size_bytes = models.BigIntegerField(
        default=0,
        verbose_name="Tamaño del archivo (bytes)"
    )

    # Ingesta y almacenamiento
    ingestion_source = models.CharField(
        max_length=40,
        choices=INGESTION_SOURCES,
        default='FIREBASE_DIRECT',
        verbose_name="Origen de la ingesta"
    )
    file = models.FileField(
        upload_to='knowledge_docs/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Archivo local (opcional/desarrollo)",
        help_text="Permite pruebas locales sin bucket configurado"
    )
    raw_text = models.TextField(
        blank=True,
        verbose_name="Texto íntegro extraído"
    )

    # Estado de indexación
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        verbose_name="Estado de indexación"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error (si falló)"
    )
    chunks_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de fragmentos indexados"
    )

    # Auditoría
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_documents',
        verbose_name="Registrado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Documento de Conocimiento"
        verbose_name_plural = "Documentos de Conocimiento"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'documento'
            slug = base_slug
            counter = 1
            while KnowledgeDocument.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class KnowledgeChunk(models.Model):
    """
    Fragmento semántico derivado de un KnowledgeDocument.
    Almacena el texto contextual y su correspondiente vector embedding en formato lista de flotantes,
    garantizando portabilidad universal (Windows local, Docker y PostgreSQL en producción sin requerir DLLs binarias externas).
    """
    document = models.ForeignKey(
        KnowledgeDocument,
        on_delete=models.CASCADE,
        related_name='chunks',
        verbose_name="Documento padre"
    )
    chunk_index = models.PositiveIntegerField(
        verbose_name="Índice del fragmento"
    )
    content = models.TextField(
        verbose_name="Contenido del fragmento"
    )
    embedding = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Vector de Embedding",
        help_text="Lista de números flotantes (vector de dimensión fija)"
    )
    token_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Conteo aproximado de tokens"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos contextuales",
        help_text="Página, capítulo, subtítulo o sección para citación"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Fragmento de Conocimiento"
        verbose_name_plural = "Fragmentos de Conocimiento"
        ordering = ['document', 'chunk_index']
        unique_together = ('document', 'chunk_index')

    def __str__(self):
        return f"{self.document.title} - Fragmento #{self.chunk_index}"


class ChatSession(models.Model):
    """
    Sesión de conversación entre un usuario/avatar y el asistente Alexia.
    Por defecto es anónima para salvaguardar la privacidad de la persona usuaria (RF-OBS-02).
    """
    CHANNEL_CHOICES = (
        ('PORTAL_WEB', 'Portal Web'),
        ('ALEXIA_AVATAR', 'Avatar Interactivo Alexia'),
        ('MOBILE_APP', 'Aplicación Móvil'),
        ('TEST_PANEL', 'Panel de Pruebas RAG'),
    )

    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="ID de Sesión (UUID)"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_sessions',
        verbose_name="Usuario autenticado (opcional)"
    )
    channel = models.CharField(
        max_length=30,
        choices=CHANNEL_CHOICES,
        default='PORTAL_WEB',
        verbose_name="Canal de interacción"
    )
    is_anonymous = models.BooleanField(
        default=True,
        verbose_name="¿Es anónima?"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de inicio")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actividad")

    class Meta:
        verbose_name = "Sesión de Chat"
        verbose_name_plural = "Sesiones de Chat"
        ordering = ['-updated_at']

    def __str__(self):
        return f"Sesión {self.session_id} ({self.get_channel_display()})"


class ChatMessage(models.Model):
    """
    Mensaje individual dentro de una sesión de conversación con Alexia.
    Registra el rol, el texto, las fuentes citadas del RAG, alertas de crisis y metadatos del avatar.
    """
    ROLE_CHOICES = (
        ('USER', 'Usuario'),
        ('ASSISTANT', 'Asistente (Alexia)'),
        ('SYSTEM', 'Sistema'),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Sesión de chat"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='USER',
        verbose_name="Rol del emisor"
    )
    content = models.TextField(
        verbose_name="Contenido del mensaje"
    )
    citations = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Citas y fuentes bibliográficas",
        help_text="Lista de fragmentos y documentos que fundamentan la respuesta"
    )
    is_crisis_detected = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="¿Crisis detectada?",
        help_text="Activado cuando el motor detecta ideación de autolesión o emergencia crítica"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos de Alexia",
        help_text="tts_clean_text, suggested_expression, latency_ms, tokens, etc."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")

    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.get_role_display()}] {self.content[:50]}..."
