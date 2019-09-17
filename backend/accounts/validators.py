"""Custom validators to preserve data integrity."""

__all__ = (
    "GroupValidator",
    "BaseUserValidation",
)

from accounts.utils import Groups

from rest_framework.validators import qs_exists
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import Group
from django.contrib.auth.base_user import AbstractBaseUser


class BaseUserValidation(object):
    """
    Base implementation of a validator that validates the group of a user.
    """

    context = None

    def __call__(self, instance):
        """
        Check the user instance that tries to be set.

        :param instance: The user instance that tries to be set
        :type instance: accounts.models.User

        :return: The validated user instance
        :rtype: accounts.models.User
        """
        if not isinstance(instance, AbstractBaseUser):
            raise ValidationError("The value is not a user or user id")

        if qs_exists(self.set_filter(instance.groups.all())):
            return instance

        raise ValidationError(
            "The current user can't be assigned to this serializer"
        )

    def set_filter(self, queryset):
        """
        Inject the appropriate filter into the queryset

        :param queryset: The queryset to filter
        :type queryset: django.db.models.query.QuerySet

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        raise NotImplementedError("This method must be overridden")

    def set_context(self, serializer):
        """
        Retrieve the context from the serializer.

        :param serializer: The current serializer instance.
        :type serializer: rest_framework.serializers.Field
        """
        setattr(self, "context", serializer.context)


class GroupValidator(BaseUserValidation):
    """
    Serializer field validator that validates that the user is a employee.
    """

    def __init__(self, ident):
        """
        Initialize the group validator.

        :param ident: The identifier of the group
        :type ident: int
        """
        self.ident = ident

    def __repr__(self):
        """
        Create a nicer representation when representing the serializer.

        :return: The nice representation
        :rtype: str
        """
        klass = self.__class__.__name__
        group = self.set_filter(Group.objects.all()).values("id").get()

        return f"{klass}(Groups.{Groups(group['id']).name})"

    def set_filter(self, queryset):
        """
        Inject the appropriate filter into the queryset

        :param queryset: The queryset to filter
        :type queryset: django.db.models.query.QuerySet

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        return queryset.filter(id=self.ident)
