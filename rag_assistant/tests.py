from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from authentication.models import UserProfile, Role
from .models import KnowledgeDocument, KnowledgeChunk, ChatSession, ChatMessage


class RAGAssistantTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Superadmin
        self.superadmin = User.objects.create_superuser(
            username='admin_rag',
            email='admin_rag@lxia.org',
            password='Password123*'
        )
        self.superadmin_profile, _ = UserProfile.objects.get_or_create(user=self.superadmin)
        self.superadmin_profile.role = Role.SUPERADMIN
        self.superadmin_profile.save()
        self.superadmin_token, _ = Token.objects.get_or_create(user=self.superadmin)

        # 2. Investigador (Researcher)
        self.researcher = User.objects.create_user(
            username='investigador_rag',
            email='investigador_rag@lxia.org',
            password='Password123*'
        )
        self.researcher_profile, _ = UserProfile.objects.get_or_create(user=self.researcher)
        self.researcher_profile.role = Role.RESEARCHER
        self.researcher_profile.save()
        self.researcher_token, _ = Token.objects.get_or_create(user=self.researcher)

        # 3. Gestor de contenido (sin permiso de RAG)
        self.content_manager = User.objects.create_user(
            username='cm_user',
            email='cm_user@lxia.org',
            password='Password123*'
        )
        self.cm_profile, _ = UserProfile.objects.get_or_create(user=self.content_manager)
        self.cm_profile.role = Role.CONTENT_MANAGER
        self.cm_profile.save()
        self.cm_token, _ = Token.objects.get_or_create(user=self.content_manager)

        # 4. Documento base para pruebas
        self.doc_legal = KnowledgeDocument.objects.create(
            title="Protocolo de Identidad de Género y Trámite Notarial",
            description="Directriz para la corrección del componente sexo bajo el Decreto 1227 de 2015 en Colombia.",
            document_type="LEGAL",
            ingestion_source="MANUAL_TEXT",
            raw_text=(
                "El Decreto 1227 de 2015 permite que las personas mayores de edad soliciten la corrección "
                "del componente sexo en el registro civil ante cualquier notaría de Colombia. "
                "Para este trámite solo se requiere la presentación de la cédula de ciudadanía y una declaración "
                "bajo la gravedad de juramento indicando la voluntad de cambio. No se requieren exámenes médicos "
                "ni dictámenes psiquiátricos previos."
            ),
            uploaded_by=self.researcher
        )

        self.webhook_secret = getattr(settings, 'CLOUD_FUNCTION_WEBHOOK_SECRET', 'lxia-cloud-func-secret-key-2026')

    # ========================================================================
    # 1. PRUEBAS DE PERMISOS Y REGISTRO EN BASE DE CONOCIMIENTO
    # ========================================================================

    def test_anonymous_cannot_manage_knowledge_documents(self):
        """Usuarios anónimos no pueden listar ni registrar fuentes documentales."""
        res_list = self.client.get('/api/v1/knowledge/documents/')
        self.assertEqual(res_list.status_code, status.HTTP_401_UNAUTHORIZED)

        res_create = self.client.post('/api/v1/knowledge/documents/', {
            "title": "Documento No Autorizado"
        })
        self.assertEqual(res_create.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_content_manager_forbidden_from_knowledge_documents(self):
        """Usuarios con rol distinto a Investigador o Superadmin reciben 403 Forbidden."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cm_token.key}')
        res = self.client.get('/api/v1/knowledge/documents/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_researcher_can_create_document_with_firebase_url(self):
        """
        Un investigador puede registrar un documento indicando la URL de Firebase Storage
        sin enviar binarios multipart (0 MB de ancho de banda en Render).
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.researcher_token.key}')
        payload = {
            "title": "Guía Clínica de Terapia Hormonal 2026",
            "description": "Lineamientos de dosificación y seguimiento endocrinológico.",
            "document_type": "PROTOCOL",
            "ingestion_source": "FIREBASE_DIRECT",
            "file_url": "https://firebasestorage.googleapis.com/v0/b/lxia-app.appspot.com/o/guia_hormonas.pdf?alt=media",
            "storage_path": "knowledge_docs/2026/guia_hormonas.pdf",
            "file_size_bytes": 2048576  # ~2 MB
        }
        res = self.client.post('/api/v1/knowledge/documents/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], payload['title'])
        self.assertEqual(res.data['status'], 'PENDING')
        self.assertEqual(res.data['storage_path'], payload['storage_path'])

    # ========================================================================
    # 2. PRUEBAS DE INDEXACIÓN Y BÚSQUEDA VECTORIAL
    # ========================================================================

    def test_trigger_index_creates_chunks_and_embeddings(self):
        """Disparar el endpoint /index/ procesa el documento y genera fragmentos vectorizados."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.researcher_token.key}')
        res = self.client.post(f'/api/v1/knowledge/documents/{self.doc_legal.id}/index/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertGreaterEqual(res.data['chunks_count'], 1)

        self.doc_legal.refresh_from_db()
        self.assertEqual(self.doc_legal.status, 'INDEXED')
        self.assertEqual(self.doc_legal.chunks.count(), res.data['chunks_count'])

        # Verificar que los fragmentos tengan vector de embedding no vacío
        first_chunk = self.doc_legal.chunks.first()
        self.assertGreater(len(first_chunk.embedding), 0)

    def test_test_search_endpoint(self):
        """Endpoint de prueba de búsqueda vectorial devuelve resultados con similitud de coseno."""
        # Indexar documento primero
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.researcher_token.key}')
        self.client.post(f'/api/v1/knowledge/documents/{self.doc_legal.id}/index/')

        payload = {
            "query": "notaría trámite de cambio de sexo decreto 1227",
            "top_k": 3,
            "threshold": 0.10
        }
        res = self.client.post('/api/v1/knowledge/test-search/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data['total_matches'], 1)
        self.assertIn('score', res.data['results'][0])
        self.assertGreater(res.data['results'][0]['score'], 0.10)

    # ========================================================================
    # 3. PRUEBAS DEL WEBHOOK PARA CLOUD FUNCTIONS (SERVERLESS)
    # ========================================================================

    def test_cloud_function_webhook_requires_valid_secret(self):
        """El webhook rechaza peticiones sin la cabecera X-Webhook-Secret o con clave inválida."""
        payload = {
            "storage_path": "knowledge_docs/test.pdf",
            "extracted_text": "Texto extraído por Cloud Function"
        }
        # Sin cabecera
        res_no_secret = self.client.post('/api/v1/knowledge/webhook/document-extracted/', payload, format='json')
        self.assertEqual(res_no_secret.status_code, status.HTTP_403_FORBIDDEN)

        # Con cabecera incorrecta
        res_bad_secret = self.client.post(
            '/api/v1/knowledge/webhook/document-extracted/',
            payload,
            format='json',
            HTTP_X_WEBHOOK_SECRET='clave-falsa'
        )
        self.assertEqual(res_bad_secret.status_code, status.HTTP_403_FORBIDDEN)

    def test_cloud_function_webhook_indexes_document_cleanly(self):
        """La Cloud Function entrega texto ya extraído y el webhook lo vectoriza e indexa sin reprocesar binarios."""
        doc_firebase = KnowledgeDocument.objects.create(
            title="Guía Salud Mental Comunitaria",
            storage_path="knowledge_docs/salud_mental.pdf",
            ingestion_source="FIREBASE_DIRECT"
        )

        payload = {
            "document_id": doc_firebase.id,
            "storage_path": doc_firebase.storage_path,
            "extracted_text": "La salud mental integral en identidades no binarias requiere espacios seguros y contención comunitaria.",
            "pages_data": [
                {"page": 1, "text": "La salud mental integral en identidades no binarias requiere espacios seguros y contención comunitaria."}
            ]
        }

        res = self.client.post(
            '/api/v1/knowledge/webhook/document-extracted/',
            payload,
            format='json',
            HTTP_X_WEBHOOK_SECRET=self.webhook_secret
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])

        doc_firebase.refresh_from_db()
        self.assertEqual(doc_firebase.status, 'INDEXED')
        self.assertEqual(doc_firebase.ingestion_source, 'CLOUD_FUNCTION_WEBHOOK')
        self.assertGreaterEqual(doc_firebase.chunks_count, 1)

    # ========================================================================
    # 4. PRUEBAS DE CONVERSACIÓN PÚBLICA, ALEXIA Y SESIONES
    # ========================================================================

    def test_public_chat_message_creates_session_and_cites_sources(self):
        """Cualquier persona puede consultar el chat sin autenticarse (anónimo); genera sesión y citas."""
        # Indexar documento para tener base de conocimiento activa
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.researcher_token.key}')
        self.client.post(f'/api/v1/knowledge/documents/{self.doc_legal.id}/index/')

        # Usuario anónimo hace pregunta
        self.client.credentials()  # Remover token
        payload = {
            "message": "¿Qué requisitos necesito para el cambio de sexo en el registro civil según el decreto 1227?"
        }
        res = self.client.post('/api/v1/chat/message/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('session_id', res.data)
        self.assertIn('content', res.data)
        self.assertFalse(res.data['is_crisis_detected'])
        self.assertGreaterEqual(len(res.data['citations']), 1)
        self.assertIn("Nota ética", res.data['content'])

        # Historial de sesión
        session_id = res.data['session_id']
        res_history = self.client.get(f'/api/v1/chat/history/{session_id}/')
        self.assertEqual(res_history.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_history.data['messages']), 2)  # 1 user + 1 assistant

    def test_alexia_avatar_dedicated_endpoint(self):
        """El endpoint de Alexia retorna metadatos optimizados de expresión visual y texto fonético TTS."""
        payload = {
            "message": "Hola Alexia, cuéntame sobre tus servicios de orientación."
        }
        res = self.client.post('/api/v1/alexia/interact/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('suggested_expression', res.data)
        self.assertIn('tts_clean_text', res.data)
        self.assertNotIn('*', res.data['tts_clean_text'])  # TTS limpio sin markdown

    # ========================================================================
    # 5. PRUEBAS DE DETECCIÓN DE CRISIS (PRIORIDAD CERO - RF-RAG-09)
    # ========================================================================

    def test_crisis_detector_immediate_referral_and_hotlines(self):
        """Mensajes con riesgo inminente de suicidio disparan alerta de crisis y entregan líneas verificadas."""
        payload = {
            "message": "Ya no puedo más con esta vida, quiero suicidarme hoy mismo"
        }
        res = self.client.post('/api/v1/chat/message/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['is_crisis_detected'])
        self.assertIn('emergency_hotlines', res.data)
        self.assertGreaterEqual(len(res.data['emergency_hotlines']), 3)

        # Verificar que incluya la Línea 106 y Línea 123
        hotline_phones = [h['phone'] for h in res.data['emergency_hotlines']]
        self.assertIn('106', hotline_phones)
        self.assertIn('123', hotline_phones)

        # Verificar registro en base de datos
        session = ChatSession.objects.get(session_id=res.data['session_id'])
        assistant_msg = session.messages.filter(role='ASSISTANT').first()
        self.assertTrue(assistant_msg.is_crisis_detected)
