"""Model factories for easy fake model creation."""

__all__ = (
    "UserFactory",
)

from django.contrib.auth.hashers import make_password

from factory import DjangoModelFactory, Faker, lazy_attribute

from accounts.models import User


class UserFactory(DjangoModelFactory):
    """
    User factory for easy model creation.

    This class will return a new user model instance
    based on fake data from faker's data lists.
    """

    class Meta:
        model = User

    first_name = Faker("first_name")
    last_name = Faker("last_name")

    @lazy_attribute
    def username(self):
        """
        Generate a username from the fake first and last name.

        :return: A 'fake' username for this user
        :rtype: str
        """
        return f"{self.first_name}-{self.last_name}".lower()

    @lazy_attribute
    def password(self):
        """
        Generate the fake password to use, this is always 'password'.

        :return: The hashed password
        :rtype: str
        """
        return make_password("password")

    @lazy_attribute
    def email(self):
        """
        Generate a fake email based on the username.

        :return: The email for this user
        :rtype: str
        """
        return f"{self.username}@example.com"
