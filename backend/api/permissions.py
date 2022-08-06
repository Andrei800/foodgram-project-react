from rest_framework import permissions


class IsAuthenticatedOwnerOrAdminOnly(permissions.BasePermission):
    message = "Access to edit only for owner or admin!"

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if (request.method in ['PATCH', 'DELETE'] and not
                request.user.is_anonymous):
            return (
                request.user == obj.author
                or request.user.is_superuser
            )
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    message = "Access only for admin!"

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)
