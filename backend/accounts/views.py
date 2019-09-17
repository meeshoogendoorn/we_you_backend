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

from rest_framework.viewsets import ViewSetMixin
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework.authentication import BasicAuthentication

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

    serializer_class = AccountSerializer
    authentication_classes = (IsAcceptable,)


class RegisterEmployerViewSet(ViewSetMixin, CreateAPIView):
    """View-set for registering a single employer."""

    serializer_class = RegisterEmployerSerializer
    permission_classes = (IsManagement,)


class RegisterEmployeesViewSet(ViewSetMixin, CreateAPIView):
    """View-set for registering new employees."""

    serializer_class = RegisterEmployeesSerializer
    permission_classes = (IsManagement | IsEmployer,)
