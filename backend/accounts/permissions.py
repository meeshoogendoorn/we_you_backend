from rest_framework.permissions import IsAuthenticated

from accounts.utils import is_management, is_employer
from accounts.utils import is_administrator, is_employee


class IsManagement(IsAuthenticated):
    """Permission for management only."""

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and from management.

        This permission will also provide (full) access to the
        administrator.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view instance
        :type view: rest_framework.views.APIView

        :return: Whether the permission was granted or not
        :rtype: bool
        """
        return (
            IsAuthenticated.has_permission(self, request, view)
            and is_management(request.user)
        )


class IsEmployer(IsAuthenticated):
    """Permission for employer only."""

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and a employer.

        This permission will also provide (full) access to the
        administrator.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view instance
        :type view: rest_framework.views.APIView

        :return: Whether the permission was granted or not
        :rtype: bool
        """
        return (
            IsAuthenticated.has_permission(self, request, view)
            and is_employer(request.user)
        )


class IsEmployee(IsAuthenticated):
    """Permission for employee only."""

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and a employee and read-only.

        This permission will also provide (full) access to the
        administrator.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view instance
        :type view: rest_framework.views.APIView

        :return: Whether the permission was granted or not
        :rtype: bool
        """
        return (
            IsAuthenticated.has_permission(self, request, view)
            and is_employee(request.user)
        )


class IsManagementAndReadOnly(IsAuthenticated):
    """Permission for management read-only."""

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and from management and read-only.

        This permission will also provide (full) access to the
        administrator.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view instance
        :type view: rest_framework.views.APIView

        :return: Whether the permission was granted or not
        :rtype: bool
        """
        if not IsAuthenticated.has_permission(self, request, view):
            return False

        if request.method.upper() in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return is_management(request.user)

        return is_administrator(request.user)


class IsEmployerAndReadOnly(IsAuthenticated):
    """Permission for employer read-only."""

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and employer and read-only.

        This permission will also provide (full) access to the
        administrator.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view instance
        :type view: rest_framework.views.APIView

        :return: Whether the permission was granted or not
        :rtype: bool
        """
        if not IsAuthenticated.has_permission(self, request, view):
            return False

        if request.method.upper() in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return is_employer(request.user)

        return is_administrator(request.user)


class IsEmployeeAndReadOnly(IsAuthenticated):
    """Permission for employee read-only."""

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and employee and read-only.

        This permission will also provide (full) access to the
        administrator.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :param view: The current view instance
        :type view: rest_framework.views.APIView

        :return: Whether the permission was granted or not
        :rtype: bool
        """
        if not IsAuthenticated.has_permission(self, request, view):
            return False

        if request.method.upper() in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return is_employee(request.user)

        return is_administrator(request.user)
