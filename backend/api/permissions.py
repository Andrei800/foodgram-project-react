from rest_framework import permissions


class IsAuthenticatedOwnerOrAdminOnly(permissions.BasePermission):
    message = "Access to edit only for owner or admin!"

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser)


class IsAdminOrReadOnly(permissions.BasePermission):
    message = "Access only for admin!"

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)
