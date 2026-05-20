from rest_framework.permissions import SAFE_METHODS, BasePermission


def role_in(user, roles):
    return bool(user and user.is_authenticated and (user.is_staff or getattr(user, "role", None) in roles))


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return role_in(request.user, {"ADMIN"})


class IsNetworkAdminOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return role_in(request.user, {"ADMIN", "NETWORK_ADMIN"})


class IsSecurityEngineerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return role_in(request.user, {"ADMIN", "SECURITY_ENGINEER"})


class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return role_in(request.user, {"ADMIN"})


class CanRunDetection(BasePermission):
    def has_permission(self, request, view):
        return role_in(request.user, {"ADMIN", "NETWORK_ADMIN", "SECURITY_ENGINEER", "STUDENT"})


class CanApproveResponse(BasePermission):
    def has_permission(self, request, view):
        return role_in(request.user, {"ADMIN", "NETWORK_ADMIN"})


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return role_in(request.user, {"ADMIN"})


class IsAdminUserForUnsafe(BasePermission):
    def has_permission(self, request, view):
        return role_in(request.user, {"ADMIN"})
