from rest_framework import permissions


class IsAuthorPermission(permissions.BasePermission):
    """Праверка на авторство для DELETE и PATCH запросов к рецепту."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
