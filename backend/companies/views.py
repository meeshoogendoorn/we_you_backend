"""Company related views and viewsets."""

__all__ = (
    "CompanyViewSet",
    "CompanyLogoViewSet",
    "ColourThemeViewSet",
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import DjangoModelPermissions

from accounts.utils import is_administrator
from accounts.permissions import IsManagementAndReadOnly
from accounts.permissions import IsEmployeeAndReadOnly, IsEmployer

from companies.models import ColourTheme, Company
from companies.serializers import ColourThemeSerializer, CompanySerializer

from utilities.models import Image
from utilities.serializers import ImageSerializer


class CompanyViewSet(ModelViewSet):
    """ViewSet for companies."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions)


class ColourThemeViewSet(ModelViewSet):
    queryset = ColourTheme.objects.all()
    serializer_class = ColourThemeSerializer

    permission_classes = (
        IsEmployer | IsEmployeeAndReadOnly | IsManagementAndReadOnly
    )

    def get_serializer(self, *args, **kwargs):
        """
        Overridden to add the company when possible.

        We can't add a company for a administrator because we
        won't require it to have one.
        """
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()

        if not is_administrator(self.request.user):
            company = self.request.user.member.company
            kwargs = {**kwargs, "company": company}

        return serializer_class(*args, **kwargs)


class CompanyLogoViewSet(ModelViewSet):
    """ViewSet for the company logo."""

    serializer_class = ImageSerializer

    def get_queryset(self):
        """
        Retrieve the permission filtered queryset.

        :return: The image queryset
        :rtype: django.db.models.query.QuerySet
        """
        return Image.objects.filter(
            colourtheme__company__member__account=self.request.user
        )
