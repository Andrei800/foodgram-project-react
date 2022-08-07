from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthenticatedOwnerOnly(BasePermission):
    message = "Access to edit only for owner!"
    methods = ['POST', 'DELETE', 'PUT', 'PATCH']

    def has_permission(self, request, view):
        user = request.user
        method = request.method
        if method == 'GET':
            return True
        elif method in self.methods and user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        method = request.method
        if method == 'GET':
            return True
        elif obj.author == user and method in ['DELETE', 'PUT', 'PATCH']:
            return True
        return False


class IsAdminOrReadOnly(BasePermission):
    message = "Access only for admin!"

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user and request.user.is_staff)
