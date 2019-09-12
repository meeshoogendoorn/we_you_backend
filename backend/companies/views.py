"""Company related views and viewsets."""

__all__ = (
    "CompanyViewSet",
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import DjangoModelPermissions

from companies.models import Company
from companies.serializers import CompanySerializer


class CompanyViewSet(ModelViewSet):
    """ViewSet for companies."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
