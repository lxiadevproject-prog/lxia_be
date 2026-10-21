from rest_framework import permissions


def _get_profile(user):
    return getattr(user, 'profile', None)


class IsSuperadmin(permissions.BasePermission):
    """Permiso exclusivo para Superadministradores."""
    message = "Acceso restringido a Superadministradores del sistema."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = _get_profile(request.user)
        return request.user.is_superuser or (profile and profile.is_superadmin)


class IsResearcher(permissions.BasePermission):
    """Permiso para el Equipo de Investigación (gestión de IA/RAG) o Superadmin."""
    message = "Acceso restringido a miembros del Equipo de Investigación o Superadministradores."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = _get_profile(request.user)
        return request.user.is_superuser or (profile and profile.is_researcher)


class IsContentManager(permissions.BasePermission):
    """Permiso para Administradores de Contenido (gestión de portal web) o Superadmin."""
    message = "Acceso restringido a Administradores de Contenido o Superadministradores."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = _get_profile(request.user)
        return request.user.is_superuser or (profile and profile.is_content_manager)


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permite lectura libre (GET, HEAD, OPTIONS).
    Restringe escrituras (POST, PUT, PATCH, DELETE) a usuarios con rol administrativo.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        profile = _get_profile(request.user)
        return request.user.is_superuser or (profile and (profile.is_content_manager or profile.is_researcher))
