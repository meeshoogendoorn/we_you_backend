"""Custom validators for comminucation purposes."""

__all__ = (
    "DefaultEmailRestrictions",
)

from rest_framework.exceptions import ValidationError


class DefaultEmailRestrictions(object):
    """Validate that default emails don't get deleted."""

    def __init__(self):
        """Initialize the instance."""
        self.is_delete = False

    def __call__(self, company):
        """
        Actually validate the value.

        :param company: The company to validate
        :type company: companies.models.Company | None

        :return: The validated value
        :rtype: companies.models.Company

        :raises ValidationError: When the company is tried to be deleted
        """
        if self.is_delete and company is None:
            raise ValidationError("May not delete default email")

        return company

    def set_context(self, serializer):
        """
        Check if the current request

        :param serializer: The current serializer field
        :type serializer: rest_framework.serializers.Field
        """
        self.is_delete = serializer.context.request.method == "DELETE"
