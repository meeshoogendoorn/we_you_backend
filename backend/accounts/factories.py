"""Model factories for easy fake model creation."""

__all__ = (
    "UserFactory",
    "AuthFactory",
)

from factory import Iterator, Faker
from factory import DjangoModelFactory

from knox.models import AuthToken

from accounts.models import Group, User


class UserFactory(DjangoModelFactory):
    """
    User factory for easy model creation.

    This class will return a new user model instance
    based on fake data from faker's data lists.
    """

    class Meta:
        model = User

    email = Faker("email")
    group = Iterator(Group.objects.all())

    password = "password"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Overridden to user the managers create_user() method.

        :param model_class: The class of the model to use
        :type model_class: type of accounts.models.User

        :param args: The additional arguments for field values
        :type args: str | int | bool | datetime.datetime

        :param args: The additional keyword arguments for field values
        :type args: str | int | bool | datetime.datetime

        :return: The newly created user
        :rtype: accounts.models.User
        """
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class AuthFactory(DjangoModelFactory):
    """Auth token factory for easy model creation."""

    class Meta:
        model = AuthToken

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Overridden to append the plain token for usage.

        :param model_class: The class of the model to use
        :type model_class: type of knox.models.AuthToken

        :param args: The additional arguments for field values
        :type args: str | int | bool | datetime.datetime

        :param args: The additional keyword arguments for field values
        :type args: str | int | bool | datetime.datetime

        :return: The newly created token
        :rtype: knox.models.AuthToken
        """
        manager = cls._get_manager(model_class)
        instance, token = manager.create(*args, **kwargs)

        setattr(instance, "plain", token)
        return instance
