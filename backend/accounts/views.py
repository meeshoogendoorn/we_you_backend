"""Account specific REST apis"""

__all__ = (
    "LoginView",
    "LogoutView",
    "RegisterEmployerViewSet",
    "RegisterEmployeesViewSet",
)

from knox.views import LoginView as BaseLoginView
from knox.views import LogoutView

from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.authentication import BasicAuthentication

from accounts.serializers import RegisterEmployerSerializer
from accounts.serializers import RegisterEmployeesSerializer
from accounts.permissions import IsEmployer, IsAdmin


class LoginView(BaseLoginView):
    """Overridden login view for HTTP basic authentication."""
    authentication_classes = (BasicAuthentication,)


class RegisterEmployerViewSet(ViewSetMixin, CreateAPIView):
    """"""

    serializer_class = RegisterEmployerSerializer
    permission_classes = (IsAdmin,)


class RegisterEmployeesViewSet(ViewSetMixin, CreateAPIView):
    """Viewset for registering new employees."""

    serializer_class = RegisterEmployeesSerializer
    permission_classes = (IsEmployer | IsAdmin)
