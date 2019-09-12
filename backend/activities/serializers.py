"""Activity related serializers."""

__all__ = (
    "ColourThemeSerializer",
)

from rest_framework.serializers import ModelSerializer

from activities.models import Answer
from activities.models import Question
from activities.models import ColourTheme
from activities.models import QuestionSet
from activities.models import QuestionTheme

from companies.models import Company
from utilities.fields import HyperlinkedRelatedReadField


class ColourThemeSerializer(ModelSerializer):
    """
    Serializer for the main colour theme.

    XXX MAYBE: move all colour theme related classes to company?
    """
    class Meta:
        model = ColourTheme
        fields = ("id", "company", "primary", "accent")

    company = HyperlinkedRelatedReadField(
        queryset=Company.objects.all(),
        view_name="company-detail",
    )
