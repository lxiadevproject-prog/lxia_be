from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from authentication.models import UserProfile, Role
from .models import Category, Tag, Article, Resource


class ContentManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Superadmin user
        self.superadmin = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@lxia.org',
            password='Password123*'
        )
        self.superadmin_profile, _ = UserProfile.objects.get_or_create(user=self.superadmin)
        self.superadmin_profile.role = Role.SUPERADMIN
        self.superadmin_profile.save()
        self.superadmin_token, _ = Token.objects.get_or_create(user=self.superadmin)

        # 2. Content Manager user
        self.content_manager = User.objects.create_user(
            username='gestor_contenido',
            email='gestor@lxia.org',
            password='Password123*'
        )
        self.cm_profile, _ = UserProfile.objects.get_or_create(user=self.content_manager)
        self.cm_profile.role = Role.CONTENT_MANAGER
        self.cm_profile.save()
        self.cm_token, _ = Token.objects.get_or_create(user=self.content_manager)

        # 3. Regular / Researcher user
        self.researcher = User.objects.create_user(
            username='investigador',
            email='investigador@lxia.org',
            password='Password123*'
        )
        self.researcher_profile, _ = UserProfile.objects.get_or_create(user=self.researcher)
        self.researcher_profile.role = Role.RESEARCHER
        self.researcher_profile.save()
        self.researcher_token, _ = Token.objects.get_or_create(user=self.researcher)

        # 4. Datos base de prueba
        self.category_salud = Category.objects.create(
            name='Salud y Bienestar',
            description='Artículos sobre cuidado de la salud física y mental',
            icon='heart',
            order=1,
            is_active=True
        )
        self.category_inactiva = Category.objects.create(
            name='Sección en Construcción',
            is_active=False
        )

        self.tag_autocuidado = Tag.objects.create(name='Autocuidado')
        self.tag_salud = Tag.objects.create(name='Salud Mental')

        # Artículo publicado
        self.article_published = Article.objects.create(
            title='Guía de Autocuidado para Personas Trans',
            summary='Resumen sobre estrategias prácticas de autocuidado y acompañamiento emocional.',
            body='Este es el cuerpo completo de la guía de autocuidado con múltiples recomendaciones...',
            category=self.salud_category if hasattr(self, 'salud_category') else self.category_salud,
            status=Article.Status.PUBLISHED,
            author=self.content_manager
        )
        self.article_published.tags.add(self.tag_autocuidado)

        # Artículo borrador
        self.article_draft = Article.objects.create(
            title='Borrador en revisión sobre derechos en salud',
            summary='Resumen del borrador no visible para el público.',
            body='Contenido confidencial o en borrador.',
            category=self.category_salud,
            status=Article.Status.DRAFT,
            author=self.content_manager
        )

    def test_category_auto_slug_and_ordering(self):
        """Verifica que el slug se genere automáticamente y el orden sea respetado."""
        cat = Category.objects.create(name='Derechos e Identidad')
        self.assertEqual(cat.slug, 'derechos-e-identidad')

    def test_public_category_list_hides_inactive(self):
        """Usuarios anónimos solo ven categorías activas."""
        url = reverse('content-category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [c['slug'] for c in response.data['results']]
        self.assertIn('salud-y-bienestar', slugs)
        self.assertNotIn('seccion-en-construccion', slugs)

    def test_public_article_list_only_shows_published(self):
        """El portal público solo lista artículos con status=PUBLISHED (RF-CNT-01)."""
        url = reverse('content-article-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [a['slug'] for a in response.data['results']]
        self.assertIn(self.article_published.slug, slugs)
        self.assertNotIn(self.article_draft.slug, slugs)

    def test_public_article_detail_increments_views(self):
        """Consultar el detalle de un artículo incrementa el contador de lecturas y retorna el body."""
        initial_views = self.article_published.views_count
        url = reverse('content-article-detail', kwargs={'slug': self.article_published.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('body', response.data)
        self.assertEqual(response.data['views_count'], initial_views + 1)

    def test_filter_articles_by_category_and_search(self):
        """Verifica filtros por categoría y búsqueda de texto."""
        url = f"{reverse('content-article-list')}?category__slug={self.category_salud.slug}&search=Autocuidado"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_anonymous_cannot_create_article_in_cms(self):
        """Usuarios anónimos no pueden crear artículos en el endpoint CMS /manage/articles/."""
        url = reverse('manage-article-list')
        payload = {
            'title': 'Intento no autorizado',
            'summary': 'Resumen',
            'body': 'Cuerpo',
            'category': self.category_salud.id
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_researcher_cannot_create_article(self):
        """Un investigador (solo RAG) no puede crear artículos en el CMS del portal (403)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.researcher_token.key}')
        url = reverse('manage-article-list')
        payload = {
            'title': 'Intento investigador',
            'summary': 'Resumen',
            'body': 'Cuerpo',
            'category': self.category_salud.id
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_content_manager_can_create_and_publish_article(self):
        """Un Gestor de Contenidos puede crear un borrador y luego publicarlo."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cm_token.key}')
        url = reverse('manage-article-list')
        payload = {
            'title': 'Nuevo Artículo sobre Acompañamiento',
            'summary': 'Resumen breve para vista móvil',
            'body': 'Texto enriquecido que explica cómo acompañar a personas trans en su proceso familiar.',
            'category': self.category_salud.id,
            'tags': [self.tag_autocuidado.id],
            'status': 'DRAFT'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_id = response.data['id']
        self.assertEqual(response.data['status'], 'DRAFT')
        self.assertEqual(response.data['author_name'], 'gestor_contenido')

        # Publicar artículo con la acción /publish/
        publish_url = reverse('manage-article-publish', kwargs={'pk': new_id})
        publish_res = self.client.post(publish_url)
        self.assertEqual(publish_res.status_code, status.HTTP_200_OK)
        self.assertEqual(publish_res.data['status'], 'PUBLISHED')
        self.assertIsNotNone(publish_res.data['published_at'])

    def test_resource_creation_and_track_download(self):
        """Verifica la creación de un recurso externo y el conteo de descargas."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cm_token.key}')
        url = reverse('content-resource-list')
        payload = {
            'title': 'Directorio de Centros de Salud Aliados',
            'description': 'Directorio nacional en línea',
            'resource_type': 'EXTERNAL_LINK',
            'external_url': 'https://ejemplo.org/directorio-salud',
            'category': self.category_salud.id,
            'is_featured': True
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resource_id = response.data['id']

        # Limpiar credenciales y probar track-download de forma anónima
        self.client.credentials()
        track_url = reverse('content-resource-track-download', kwargs={'pk': resource_id})
        track_res = self.client.post(track_url)
        self.assertEqual(track_res.status_code, status.HTTP_200_OK)
        self.assertEqual(track_res.data['download_count'], 1)
