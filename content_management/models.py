import math
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    """
    Categorías temáticas para organizar los contenidos y guías del portal web
    (ej. Salud mental, Trámites de identidad, Redes comunitarias, Autocuidado).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Nombre del ícono para el frontend (ej. 'heart', 'shield', 'book-open')",
        verbose_name="Ícono"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de despliegue")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Tag(models.Model):
    """
    Etiquetas transversales para clasificación libre y búsqueda de artículos.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=60, unique=True, blank=True, verbose_name="Slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Article(models.Model):
    """
    Artículos y guías de autocuidado de la plataforma TransLúcidas.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        PUBLISHED = 'PUBLISHED', 'Publicado'
        ARCHIVED = 'ARCHIVED', 'Archivado'

    title = models.CharField(max_length=255, verbose_name="Título")
    slug = models.SlugField(max_length=280, unique=True, blank=True, db_index=True, verbose_name="Slug")
    summary = models.TextField(
        max_length=500,
        help_text="Resumen conciso optimizado para carga rápida en redes móviles y vista previa",
        verbose_name="Resumen"
    )
    body = models.TextField(help_text="Contenido completo del artículo en formato Markdown o HTML", verbose_name="Cuerpo")
    featured_image = models.ImageField(
        upload_to='articles/',
        blank=True,
        null=True,
        verbose_name="Imagen de portada"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name="Categoría"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name="Etiquetas")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_articles',
        verbose_name="Autor / Gestor"
    )
    reading_time_minutes = models.PositiveSmallIntegerField(
        default=3,
        help_text="Tiempo estimado de lectura en minutos",
        verbose_name="Tiempo de lectura (min)"
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name="Cantidad de lecturas")
    published_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="Fecha de publicación")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Generar slug único si no existe
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Calcular tiempo estimado de lectura (promedio 200 palabras por minuto)
        if self.body:
            words = len(self.body.split())
            self.reading_time_minutes = max(1, math.ceil(words / 200))

        # Asignar fecha de publicación si cambia a publicado y no tiene fecha previa
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)


class Resource(models.Model):
    """
    Recursos complementarios (guías descargables en PDF, enlaces de emergencia, infografías, audios).
    """
    class ResourceType(models.TextChoices):
        PDF = 'PDF', 'Documento PDF descargable'
        INFOGRAPHIC = 'INFOGRAPHIC', 'Infografía / Imagen'
        EXTERNAL_LINK = 'EXTERNAL_LINK', 'Enlace externo'
        AUDIO = 'AUDIO', 'Audio / Podcast'

    title = models.CharField(max_length=255, verbose_name="Título")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.PDF,
        verbose_name="Tipo de recurso"
    )
    file = models.FileField(upload_to='resources/', blank=True, null=True, verbose_name="Archivo descargable")
    external_url = models.URLField(blank=True, null=True, verbose_name="Enlace externo")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        verbose_name="Categoría asociada"
    )
    is_featured = models.BooleanField(default=False, db_index=True, verbose_name="Destacado en portal")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Descargas / Accesos")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_resource_type_display()}]"
