"""Url patterns for the accounts app."""

__all__ = (
    "urlpatterns",
)

from django.urls import path

from rest_framework.routers import SimpleRouter

from accounts.views import UserView
from accounts.views import AccountViewSet
from accounts.views import LogoutView, LoginView
from accounts.views import RegisterEmployerViewSet
from accounts.views import RegisterEmployeesViewSet

router = SimpleRouter()

router.register(
    "account",
    AccountViewSet,
    "account"
)

router.register(
    "register-employers",
    RegisterEmployerViewSet,
    "register-employers"
)

router.register(
    "register-employees",
    RegisterEmployeesViewSet,
    "register-employees"
)

urlpatterns = router.urls + [
    path("user/", UserView.as_view(), name="user"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
