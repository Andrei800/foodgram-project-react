from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthenticatedOwnerOnly(BasePermission):
    message = "Access to edit only for owner!"

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    obj.author == request.user
                )
            )
        )


class IsAdminOrReadOnly(BasePermission):
    message = "Access only for admin!"

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user and request.user.is_staff)
