"""Custom validators to preserve data integrity."""

__all__ = (
    "GroupValidator",
    "BaseGroupValidation",
)

from accounts.utils import Groups
from accounts.models import User

from rest_framework.exceptions import ValidationError


class BaseGroupValidation(object):
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
        if not isinstance(instance, User):
            raise ValidationError("The value is not a user instance")

        if self.has_group(instance):
            return instance

        raise ValidationError(
            "The current user can't be assigned to this serializer"
        )

    def has_group(self, instance):
        """
        Validate that the user has the appropriate group.

        Please note that this class is for data integrity, so
        even when a user is a administrator we will not allow
        it.

        :param instance: The user instance to check
        :type instance: accounts.models.User

        :return: Whether the user is in the correct group or not
        :rtype: bool
        """
        raise NotImplementedError("This method must be overridden")

    def set_context(self, serializer):
        """
        Retrieve the context from the serializer.

        :param serializer: The current serializer instance.
        :type serializer: rest_framework.serializers.Field
        """
        setattr(self, "context", serializer.context)


class GroupValidator(BaseGroupValidation):
    """
    Serializer field validator that validates that the user is a employee.
    """

    def __init__(self, ident):
        """
        Initialize the group validator.

        :param ident: The identifier of the group
        :type ident: int
        """
        assert not (isinstance(ident, int) and ident in Groups.__iter__()), (
            "The identifier of the group must be of type 'int'"
            " and defined in 'accounts.utils.Groups' to assure"
            " that it even exists"
        )

        self.ident = ident

    def __repr__(self):
        """
        Create a nicer representation when representing the serializer.

        :return: The nice representation
        :rtype: str
        """
        klass = self.__class__.__name__
        group = Groups(self.ident).name

        return f"{klass}(Groups.{group})"

    def has_group(self, instance):
        """
        Validate that the user has the appropriate group.

        Please note that this class is for data integrity, so
        even when a user is a administrator we will not allow
        it.

        :param instance: The user instance to check
        :type instance: accounts.models.User

        :return: Whether the user is in the correct group or not
        :rtype: bool
        """
        return instance.group_id == self.ident
