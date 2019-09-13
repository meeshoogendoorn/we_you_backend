"""Company related models."""

__all__ = (
    "CompanySerializer",
    "ColourThemeSerializer",
)

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import HyperlinkedRelatedField

from companies.models import ColourTheme, Company
from utilities.models import Image
from utilities.fields import HyperlinkedRelatedReadField


class CompanySerializer(ModelSerializer):
    """Serializer for a single company."""

    class Meta:
        model = Company
        fields = ("id", "name")


class ColourThemeSerializer(ModelSerializer):
    """
    Serializer for the main colour theme.
    """
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
