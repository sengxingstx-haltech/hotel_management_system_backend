from rest_framework import permissions


class HotelPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action in ['list', 'retrieve']:
            # Check if the user has the "view_user" permission for "GET" methods
            # return request.user.has_perm('auth.view_user')

            # Check if the user is in the group that has "view_user" permission for "GET" methods
            return request.user.groups.filter(permissions__codename='view_hotel').exists()
        elif view.action == 'create':
            return request.user.groups.filter(permissions__codename='add_hotel').exists()
        elif view.action == 'update':
            return request.user.groups.filter(permissions__codename='change_hotel').exists()
        elif view.action == 'destroy':
            return request.user.groups.filter(permissions__codename='delete_hotel').exists()
        else:
            # Default to not allowing other actions
            return False


class StaffPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action in ['list', 'retrieve']:
            # Check if the user has the "view_user" permission for "GET" methods
            # return request.user.has_perm('auth.view_user')

            # Check if the user is in the group that has "view_user" permission for "GET" methods
            return request.user.groups.filter(permissions__codename='view_staff').exists()
        elif view.action == 'create':
            return request.user.groups.filter(permissions__codename='add_staff').exists()
        elif view.action == 'update':
            return request.user.groups.filter(permissions__codename='change_staff').exists()
        elif view.action == 'destroy':
            return request.user.groups.filter(permissions__codename='delete_staff').exists()
        else:
            # Default to not allowing other actions
            return False
