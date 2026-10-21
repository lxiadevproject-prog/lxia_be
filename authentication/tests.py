from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import UserProfile, Role
from .signals import ROLE_GROUP_MAPPING


class AuthenticationModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Asegurar grupos creados
        for group_name in ROLE_GROUP_MAPPING.values():
            Group.objects.get_or_create(name=group_name)

        # Crear Superadmin (su perfil SUPERADMIN se crea automáticamente por la señal)
        self.superadmin = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='Password123!'
        )

        # Crear Investigador
        self.researcher = User.objects.create_user(
            username='researcher_test',
            email='researcher@test.com',
            password='Password123!'
        )
        UserProfile.objects.create(
            user=self.researcher,
            role=Role.RESEARCHER
        )

        # Crear Administrador de Contenidos
        self.content_mgr = User.objects.create_user(
            username='content_test',
            email='content@test.com',
            password='Password123!'
        )
        UserProfile.objects.create(
            user=self.content_mgr,
            role=Role.CONTENT_MANAGER
        )

    def test_user_signals_create_token_and_group(self):
        """Verifica que el usuario se sincronice con el grupo correspondiente."""
        self.assertTrue(self.researcher.groups.filter(name='Researcher').exists())
        self.assertTrue(self.content_mgr.groups.filter(name='ContentManager').exists())
        self.assertTrue(Token.objects.filter(user=self.researcher).exists())

    def test_login_success(self):
        """Inicio de sesión exitoso devuelve token y datos de usuario."""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'researcher_test',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'researcher_test')
        self.assertEqual(response.data['user']['profile']['role'], Role.RESEARCHER)

    def test_login_invalid_credentials(self):
        """Credenciales incorrectas devuelven HTTP 400."""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'researcher_test',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_endpoint_authenticated(self):
        """Endpoint /me/ requiere token y retorna información correcta."""
        token = Token.objects.get(user=self.researcher)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'researcher_test')

    def test_me_endpoint_unauthenticated(self):
        """Endpoint /me/ rechaza usuarios anónimos con 401."""
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        """Cerrar sesión invalida el token actual."""
        token = Token.objects.get(user=self.researcher)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.researcher).exists())

    def test_superadmin_can_create_user(self):
        """Superadmin puede crear usuarios con roles."""
        token = Token.objects.get(user=self.superadmin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        payload = {
            'username': 'nuevo_investigador',
            'email': 'nuevo@test.com',
            'first_name': 'Ana',
            'last_name': 'Pérez',
            'password': 'NewPassword123!',
            'role': Role.RESEARCHER,
            'institution': 'Universidad Nacional'
        }
        response = self.client.post('/api/v1/auth/users/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_created = User.objects.get(username='nuevo_investigador')
        self.assertEqual(user_created.profile.role, Role.RESEARCHER)
        self.assertEqual(user_created.profile.institution, 'Universidad Nacional')

    def test_non_superadmin_cannot_access_user_management(self):
        """Investigadores o administradores de contenido no pueden crear otros usuarios."""
        token = Token.objects.get(user=self.content_mgr)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.get('/api/v1/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
