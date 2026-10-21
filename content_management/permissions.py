from rest_framework import permissions
from authentication.permissions import _get_profile, IsContentManager


class IsContentManagerOrReadOnly(permissions.BasePermission):
    """
    Permite acceso de lectura público (SAFE_METHODS: GET, HEAD, OPTIONS).
    Restringe operaciones de creación/modificación/eliminación exclusivamente a
    usuarios autenticados con rol CONTENT_MANAGER o SUPERADMIN.
    """
    message = "Debes tener rol de Administrador de Contenido o Superadmin para realizar esta acción."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        profile = _get_profile(request.user)
        return request.user.is_superuser or (profile and (profile.is_content_manager or profile.is_superadmin))
