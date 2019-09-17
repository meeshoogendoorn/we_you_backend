"""Account related models and relations."""

__all__ = (
    "User",
    "Group",
)

from django.db.models.fields import BooleanField, EmailField
from django.db.models.fields.related import ManyToManyField

from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import Group
from django.contrib.auth.base_user import AbstractBaseUser

from accounts.managers import UserManager


class User(AbstractBaseUser):
    """Overridden django user model."""

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()

    email = EmailField(_("email address"), unique=True)

    groups = ManyToManyField(
        Group,
        blank=True,
        verbose_name=_('groups'),
        related_name="users",
        related_query_name="user",
    )

    objects = UserManager()
    deleted = BooleanField(default=False)

    @property
    def is_active(self):
        """
        Check if the user is deleted or not.

        :return: Whether or not this user is deleted.
        :rtype: bool
        """
        return not self.deleted

    def clean(self):
        """
        Overridden because there is no real username.
        """
        self.email = self.__class__.objects.normalize_email(self.email)
