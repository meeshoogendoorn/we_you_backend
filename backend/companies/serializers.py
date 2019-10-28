"""Company related models."""

__all__ = (
    "MemberSerializer",
    "CompanySerializer",
    "ColourThemeSerializer",
)

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import HyperlinkedRelatedField

from accounts.utils import is_employee
from accounts.models import User

from companies.models import Company, Member
from companies.models import ColourTheme

from utilities.models import Image
from utilities.fields import HyperlinkedRelatedReadField


class MemberSerializer(ModelSerializer):
    """Serializer for the membership relation."""

    class Meta:
        model = Member
        fields = ("id", "account", "company")

    account = HyperlinkedRelatedReadField(
        queryset=User.objects.all(),
        view_name="account-detail",
    )

    company = HyperlinkedRelatedReadField(
        queryset=Company.objects.all(),
        view_name="company-detail",
    )


class CompanySerializer(ModelSerializer):
    """Serializer for a single company."""

    class Meta:
        model = Company
        fields = ("id", "name", "theme", "members")

    theme = HyperlinkedRelatedReadField(
        queryset=ColourTheme.objects.all(),
        view_name="colour-theme-detail",
    )

    members = HyperlinkedRelatedReadField(
        many=True,
        queryset=Member.objects.all(),
        view_name="member-detail",
    )

    def get_field_names(self, declared_fields, info):
        """
        Filter out the 'members' field when the user is a employee.

        :param declared_fields: A mapping of the declared fields in order
        :type declared_fields: collections.OrderedDict

        :param info: Additional information about the current models fields
        :type info: rest_framework.utils.model_meta.FieldInfo

        :return: A sequence with the fields to serialize
        :rtype: tuple
        """
        fields = ModelSerializer.get_field_names(self, declared_fields, info)
        if not is_employee(self.context["request"].user, False):
            return fields

        return tuple(field for field in fields if field != "members")


class ColourThemeSerializer(ModelSerializer):
    """Serializer for the main colour theme."""

    class Meta:
        model = ColourTheme
        fields = ("id", "company", "primary", "accent", "logo")

    company = HyperlinkedRelatedReadField(
        queryset=Company.objects.all(),
        view_name="company-detail",
    )

    logo = HyperlinkedRelatedField(
        queryset=Image.objects.all(),
        view_name="company-logo-detail",
    )
