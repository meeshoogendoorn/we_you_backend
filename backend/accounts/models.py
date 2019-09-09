"""Account related models and relations."""

__all__ = (
    "User",
)

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Overridden django user model."""
