"""Serializers related to the analytics."""

from rest_framework.fields import DecimalField
from rest_framework.fields import DateTimeField
from rest_framework.serializers import Serializer


class CompanyChartSerializer(Serializer):
    """Serializer for the charts data."""

    data = DecimalField(read_only=True, decimal_places=2, max_digits=3)
    date = DateTimeField(read_only=True)

    update = None
    create = None
