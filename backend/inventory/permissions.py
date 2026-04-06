"""
Old permissions module — replaced by stores.permissions for multi-tenant RBAC.
Kept for backward compatibility / custom per-object permissions.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Allow full access to admin users.
    Read-only access for authenticated non-admin users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
