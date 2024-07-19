from rest_framework import permissions


class HasAnyPermission(permissions.BasePermission):
    def __init__(self, required_permissions):
        self.required_permissions = required_permissions

    def has_permission(self, request, view):
        # Check if the user has any of the required permissions
        return any(request.user.has_perm(permission) for permission in self.required_permissions)
