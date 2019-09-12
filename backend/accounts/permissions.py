from rest_framework.permissions import BasePermission

from accounts.utils import is_administrator, is_employer, is_employee


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_administrator(request.user)


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return is_employer(request.user)


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return is_employee(request.user)


class IsEmployerAndReadOnly(BasePermission):
    """
    Permission for employee read-only.
    """

    def has_permission(self, request, view):
        if request.method.upper() in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return is_employer(request.user)

        return False


class IsEmployeeAndReadOnly(BasePermission):
    """
    Permission for employee read-only.
    """

    def has_permission(self, request, view):
        if request.method.upper() in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return is_employee(request.user)

        return False
