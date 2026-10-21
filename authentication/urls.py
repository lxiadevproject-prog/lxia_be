from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    LogoutView,
    MeView,
    ChangePasswordView,
    UserManagementViewSet,
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='admin-users')

urlpatterns = [
    # Autenticación y sesión
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),

    # Gestión de usuarios por Superadmin
    path('', include(router.urls)),
]
