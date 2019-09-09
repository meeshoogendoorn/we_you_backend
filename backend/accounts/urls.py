"""Url patterns for the accounts app."""

__all__ = (
    "urlpatterns",
)

from django.urls import path

from accounts.views import LogoutView, LoginView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
]
