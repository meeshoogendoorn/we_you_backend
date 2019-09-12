"""Activity related views and view-sets."""

__all__ = (
    "ColourThemeViewSet",
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from accounts.utils import is_administrator
from accounts.permissions import IsAdmin
from accounts.permissions import IsEmployeeAndReadOnly
from accounts.permissions import IsEmployer

from activities.models import ColourTheme
from activities.serializers import ColourThemeSerializer


class ColourThemeViewSet(ModelViewSet):
    queryset = ColourTheme.objects.all()
    serializer_class = ColourThemeSerializer

    permission_classes = (
        IsAuthenticated, IsEmployer | IsEmployeeAndReadOnly | IsAdmin
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

