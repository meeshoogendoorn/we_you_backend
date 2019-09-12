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
    queryset = ColourTheme
    serializer_class = ColourThemeSerializer

    permission_classes = (
        IsAuthenticated, IsEmployer | IsEmployeeAndReadOnly | IsAdmin
    )

    def get_serializer_context(self):
        """
        Overridden to add the company when possible.

        We can't add
        """
        context = ModelViewSet.get_serializer_context(self)

        if is_administrator(self.request.user):
            return context

        company =
