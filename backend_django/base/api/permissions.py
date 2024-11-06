from rest_framework.permissions import BasePermission
from django.conf import settings

class HasValidAPIToken(BasePermission):
    """
    PERMISO PERSONALIZADO
    """

    def has_permission(self, request, view):
        auth_token = request.headers.get('Authorization')

        # VERIFICAR SI EL TOKEN ESTÁ PRESENTE EN SETTINGS
        if auth_token and auth_token == f"Bearer {settings.API_AUTH_TOKEN}":
            return True  
        return False  