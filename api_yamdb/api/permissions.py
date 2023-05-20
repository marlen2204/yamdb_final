from rest_framework.permissions import (BasePermission, SAFE_METHODS,
                                        IsAuthenticatedOrReadOnly)


class AdminOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin
                )


class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin)
                )


class AdminModeratorAuthorPermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
                )

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                )
