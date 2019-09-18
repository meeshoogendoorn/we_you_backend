"""Account specific REST apis"""

__all__ = (
    "LoginView",
    "LogoutView",

    "AccountViewSet",

    "RegisterEmployerViewSet",
    "RegisterEmployeesViewSet",
)

from knox.views import LogoutView
from knox.views import LoginView as BaseLoginView

from django.db.models.query import Q

from rest_framework.viewsets import ViewSetMixin
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework.authentication import BasicAuthentication

from accounts.utils import Groups
from accounts.utils import is_employee
from accounts.utils import is_employer
from accounts.utils import is_management

from accounts.models import User

from accounts.permissions import IsEmployer
from accounts.permissions import IsAcceptable
from accounts.permissions import IsManagement

from accounts.serializers import AccountSerializer
from accounts.serializers import RegisterEmployerSerializer
from accounts.serializers import RegisterEmployeesSerializer


class LoginView(BaseLoginView):
    """Overridden login view for HTTP basic authentication."""

    authentication_classes = (BasicAuthentication,)


class AccountViewSet(ReadOnlyModelViewSet):
    """View-set for reading account info and linking."""

    queryset = User.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (IsAcceptable,)

    def filter_queryset(self, queryset):
        """
        Filter the queryset for the appropriate users.

        :param queryset: The queryset to filter
        :type queryset: django.db.models.query.QuerySet

        :return: The queryset with the appropriate allowed users
        :rtype: django.db.models.query.QuerySet
        """
        query = Q()
        if is_employee(self.request.user, False):
            query &= Q(id=self.request.user.id)

        if is_employer(self.request.user, False):
            query &= Q(group=Groups.employee)
            query &= Q(member__company=self.request.user.member.company)

        if is_management(self.request.user, False):
            query &= ~Q(group=Groups.admin)

        return queryset.filter(query)


class RegisterEmployerViewSet(ViewSetMixin, CreateAPIView):
    """View-set for registering a single employer."""

    serializer_class = RegisterEmployerSerializer
    permission_classes = (IsManagement,)


class RegisterEmployeesViewSet(ViewSetMixin, CreateAPIView):
    """View-set for registering new employees."""

    serializer_class = RegisterEmployeesSerializer
    permission_classes = (IsManagement | IsEmployer,)
