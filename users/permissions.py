from rest_framework import permissions


# Custom permission to allow superadmins full access, but read-only for others
class IsSuperAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.method in permissions.SAFE_METHODS


# Custom permission to allow staff members full access, but read-only for others
class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == "superadmin" or request.user.user_type == "staff":
            return True
        return request.method in permissions.SAFE_METHODS


# Custom permission to allow customers full access, but read-only for others
class IsCustomerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if (
            request.user.user_type == "superadmin"
            or request.user.user_type == "staff"
            or request.user.user_type == "customer"
        ):
            return True
        return request.method in permissions.SAFE_METHODS


# Custom permission to allow object owners full access, but read-only for others
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
