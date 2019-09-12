"""Custom fields to use."""

__all__ = (
    "HyperlinkedRelatedReadField",
)

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.serializers import HyperlinkedRelatedField


class HyperlinkedRelatedReadField(HyperlinkedRelatedField):
    """
    Custom Hyperlink serializer field.

    A serializer field that represents a hyperlink on
    read and accepts a pk on write.
    """

    def __init__(self, **kwargs):
        """
        Overridden to maintain PrimaryKeyRelatedField behaviour.

        :param kwargs: The keyword arguments to pass on
        :type kwargs: any
        """
        self.pk_field = kwargs.pop('pk_field', None)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        """
        Process the format of the primary key as a integer.

        :param data: The primary key to process
        :type data: int

        :return: The instance of the model to find
        :rtype: django.db.models.base.Model
        """
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)

        try:
            return self.get_queryset().get(pk=data)

        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)

        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)
