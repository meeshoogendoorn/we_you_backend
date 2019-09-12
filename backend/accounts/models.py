"""Account related models and relations."""

__all__ = (
    "User",
)

from django.db.models.fields import BooleanField, EmailField
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

from accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Overridden django user model."""

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()

    email = EmailField(_("email address"), unique=True)

    objects = UserManager()
    deleted = BooleanField(default=False)

    @property
    def is_active(self):
        return not self.deleted

    def clean(self):
        """Overridden because there is no real username."""
        self.email = self.__class__.objects.normalize_email(self.email)
