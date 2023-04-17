"""
User's permissions.
"""

from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Granted full permission for admin. Other users can only read."""

    @staticmethod
    def _is_admin(user):
        return (
            user.is_authenticated
            and user.is_admin or user.is_superuser
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or self._is_admin
        )


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Granted full permission for admin or author. Other users can only
    read.
    """

    @staticmethod
    def _is_admin(user):
        return (
            user.is_authenticated
            and user.is_admin or user.is_superuser
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or self._is_admin(request.user)
        )
