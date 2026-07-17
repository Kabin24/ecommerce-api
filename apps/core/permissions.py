"""
Custom permissions for REST Framework.
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to check if the user owns the object.
    Used for user-specific resources like profile and cart.
    """
    def has_object_permission(self, request, view, obj):
        # Allow only if the object's user is the requesting user
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow admin to perform all actions, but restrict others to read-only.
    Used for products, categories, etc.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows object owner or admin to modify the object.
    """
    def has_object_permission(self, request, view, obj):
        # Allow admin access
        if request.user and request.user.is_staff:
            return True
        # Allow owner access
        return obj.user == request.user
