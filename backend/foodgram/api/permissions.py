from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Разрешает опасные методы только автору объекта или админу."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or any([
                    obj.author == request.user,
                    request.user.is_superuser,
                    request.user.is_staff
                ]))
