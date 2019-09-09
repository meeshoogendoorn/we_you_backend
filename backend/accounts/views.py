"""Account specific REST apis"""

__all__ = (
    "LoginView",
    "LogoutView",
)

from knox.views import LoginView as BaseLoginView
from knox.views import LogoutView

from rest_framework.authentication import BasicAuthentication


class LoginView(BaseLoginView):
    """Overridden login view for HTTP basic authentication."""
    authentication_classes = (BasicAuthentication,)
