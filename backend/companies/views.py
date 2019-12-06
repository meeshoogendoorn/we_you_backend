"""Company related views and view-sets."""

__all__ = (
    "MemberViewSet",
    "CompanyViewSet",
    "CompanyLogoViewSet",
    "ColourThemeViewSet",
)

from rest_framework.viewsets import ModelViewSet

from accounts.utils import is_employee
from accounts.utils import is_management

from accounts.permissions import IsEmployer
from accounts.permissions import IsAcceptable
from accounts.permissions import IsEmployeeAndReadOnly
from accounts.permissions import IsManagementOrReadOnly
from accounts.permissions import IsManagementAndReadOnly

from companies.models import ColourTheme
from companies.models import Company, Member

from companies.serializers import MemberSerializer
from companies.serializers import CompanySerializer
from companies.serializers import ColourThemeSerializer

from utilities.models import Image
from utilities.serializers import ImageSerializer


class MemberViewSet(ModelViewSet):
    """ViewSet to forward membership relations."""

    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = (IsAcceptable,)

    def filter_queryset(self, queryset):
        """
        Filter out the memberships that aren't accessible to the user.

        :param queryset: The queryset with all the memberships
        :type queryset: django.db.models.query.QuerySet

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        if is_management(self.request.user):
            return queryset

        if is_employee(self.request.user, False):
            return queryset.filter(account=self.request.user)

        return queryset.filter(company__members__account=self.request.user)


class CompanyViewSet(ModelViewSet):
    """ViewSet for companies."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsManagementOrReadOnly,)

    def filter_queryset(self, queryset):
        """
        Filter out the companies that aren't related to the user.

        :param queryset: The queryset with all the companies
        :type queryset: django.db.models.query.QuerySet

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        if is_management(self.request.user):
            return queryset

        return queryset.filter(members__account=self.request.user)


class ColourThemeViewSet(ModelViewSet):
    """ViewSet for the companies theme."""

    queryset = ColourTheme.objects.all()
    serializer_class = ColourThemeSerializer

    permission_classes = (
        IsEmployer | IsEmployeeAndReadOnly | IsManagementAndReadOnly,
    )

    def filter_queryset(self, queryset):
        """
        Filter out the colour themes that aren't relevant to the user.

        :param queryset: The queryset to filter
        :type queryset: django.db.models.query.QuerySet

        :return: Teh filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        if is_management(self.request.user):
            return queryset

        return queryset.filter(
            company__members__account=self.request.user.id
        )


class CompanyLogoViewSet(ModelViewSet):
    """ViewSet for the company logo."""

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (IsAcceptable,)

    def filter_queryset(self, queryset):
        """
        Filter out the unrelated logo's.

        :return: The image queryset
        :rtype: django.db.models.query.QuerySet
        """
        if is_management(self.request.user):
            return queryset

        return queryset.filter(
            colourtheme__company__members__account=self.request.user
        )
