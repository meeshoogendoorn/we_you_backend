"""Company related models."""

__all__ = (
    "CompanySerializer",
)

from rest_framework.serializers import ModelSerializer

from companies.models import Company


class CompanySerializer(ModelSerializer):
    """Serializer for a single company."""

    class Meta:
        model = Company
        fields = ("id", "name")
