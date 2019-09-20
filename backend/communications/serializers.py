"""Communication related serializers."""

__all__ = (
    "EmailSerializer",
    "VariableSerializer",
    "EnvironmentSerializer",
)

from rest_framework.serializers import CharField
from rest_framework.serializers import ModelSerializer, Serializer

from companies.models import Company
from utilities.fields import HyperlinkedRelatedReadField

from communications.models import Email
from communications.validators import DefaultEmailRestrictions


class VariableSerializer(Serializer):
    """
    Custom serializer for variables.

    This serializer makes sure that a variable isn't created
    and if updating, only the name gets updated.
    """
    name = CharField(max_length=255)

    create = None
    update = None

    def save(self, **kwargs):
        """
        Custom save method to completely ignore create requests.

        :param kwargs: Additional keyword arguments (ignored)
        :type kwargs: any

        :return: The updated variable instance
        :rtype: communications.models.Variable
        """
        if self.instance is None:
            return self.instance

        self.instance.name = self.validated_data["name"]
        self.instance.save()

        return self.instance


class EnvironmentSerializer(Serializer):
    """
    Custom environment serializer.

    Just like the variable serializer makes this class sure
    that no new environments are created. This should only be
    possible through fixtures.

    It is allowed though to change the label given to the
    environment.
    """

    create = None
    update = None

    label = CharField(max_length=255)
    variables = HyperlinkedRelatedReadField(
        many=True,
        read_only=True,
        view_name=""
    )

    def save(self, **kwargs):
        """
        Custom save method to completely ignore create requests.

        :param kwargs: Additional keyword arguments (ignored)
        :type kwargs: any

        :return: The updated environment instance
        :rtype: communications.models.Environment
        """
        if self.instance is None:
            return self.instance

        self.instance.name = self.validated_data["label"]
        self.instance.save()

        return self.instance


class EmailSerializer(ModelSerializer):
    """Serializer for emails, these models make dynamic content possible."""

    class Meta:
        model = Email
        fields = ("id", "subject", "content", "environ", "company")

    environ = HyperlinkedRelatedReadField(
        queryset=Email.objects.all(),
        view_name="",
    )

    company = HyperlinkedRelatedReadField(
        queryset=Company.objects.all(),
        view_name="",
        validators=[DefaultEmailRestrictions()]
    )
