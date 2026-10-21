from django.db import models
from django.contrib.auth.models import User


class Role(models.TextChoices):
    SUPERADMIN = 'SUPERADMIN', 'Superadministrador'
    RESEARCHER = 'RESEARCHER', 'Investigador'
    CONTENT_MANAGER = 'CONTENT_MANAGER', 'Administrador de Contenido'


class UserProfile(models.Model):
    """
    Perfil extendido para usuarios del sistema administrativo y de investigación.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONTENT_MANAGER,
        help_text="Rol asignado al usuario en el sistema"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    institution = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_superadmin(self):
        return self.role == Role.SUPERADMIN or self.user.is_superuser

    @property
    def is_researcher(self):
        return self.role in [Role.RESEARCHER, Role.SUPERADMIN] or self.user.is_superuser

    @property
    def is_content_manager(self):
        return self.role in [Role.CONTENT_MANAGER, Role.SUPERADMIN] or self.user.is_superuser
