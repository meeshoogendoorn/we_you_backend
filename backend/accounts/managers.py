"""Custom user manager to support email login."""

__all__ = (
    "UserManager",
)

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user manager.

    This class allows to create users without username.
    """

    def create_user(self, email, password, **extra):
        """
        Overridden to support email-only creation.

        :param email: The email address of the user
        :type email: str

        :param password: The raw password of the user
        :type password: str

        :param extra: The value's for additional fields
        :type extra: str | int | bool | datetime.datetime

        :return: The user instance of the created user
        :rtype: accounts.models.User
        """
        user = self.model(email=email, **extra)

        user.set_password(password)

        user.clean()
        user.save(using=self._db)

        return user
