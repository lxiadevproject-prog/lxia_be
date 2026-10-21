from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

from .models import UserProfile, Role


ROLE_GROUP_MAPPING = {
    Role.SUPERADMIN: 'Superadmin',
    Role.RESEARCHER: 'Researcher',
    Role.CONTENT_MANAGER: 'ContentManager',
}


@receiver(post_save, sender=User)
def create_user_token(sender, instance, created, **kwargs):
    """Crea automáticamente un token de autenticación para cada usuario."""
    if created:
        Token.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def ensure_superuser_profile(sender, instance, created, **kwargs):
    """
    Si se crea un superusuario (ej. createsuperuser o script),
    asegura que tenga su UserProfile con rol SUPERADMIN.
    """
    if created and instance.is_superuser:
        profile, profile_created = UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': Role.SUPERADMIN}
        )
        if not profile_created and profile.role != Role.SUPERADMIN:
            profile.role = Role.SUPERADMIN
            profile.save(update_fields=['role'])


@receiver(post_save, sender=UserProfile)
def sync_user_groups(sender, instance, created, **kwargs):
    """
    Sincroniza el grupo de Django correspondiente al rol del perfil.
    """
    user = instance.user
    role_group_name = ROLE_GROUP_MAPPING.get(instance.role)

    if role_group_name:
        # Asegurar que el grupo existe
        group, _ = Group.objects.get_or_create(name=role_group_name)

        # Quitar de otros grupos de roles conocidos
        known_groups = Group.objects.filter(name__in=ROLE_GROUP_MAPPING.values())
        user.groups.remove(*known_groups)

        # Asignar el nuevo grupo
        user.groups.add(group)

        # Si el rol es SUPERADMIN, asegurar permisos de staff
        if instance.role == Role.SUPERADMIN and not user.is_staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])
