"""
Main ViewSets for communication and related.

These should only be accessible by the administrators and management.
"""

__all__ = (
    "EmailViewSet",
    "VariableViewSet",
    "EnvironmentViewSet",
)

from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from accounts.permissions import IsManagement
from communications.models import Environment, Variable, Email

from communications.serializers import EmailSerializer
from communications.serializers import VariableSerializer
from communications.serializers import EnvironmentSerializer


class VariableViewSet(
    GenericViewSet, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
):
    """Get a overview of the available variables."""

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    permission_classes = (IsManagement,)


class EnvironmentViewSet(
    GenericViewSet, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
):
    """Get a overview of the available variables."""

    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    permission_classes = (IsManagement,)


class EmailViewSet(ModelViewSet):
    """Main view set for inspecting, creating and updating emails."""

    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    permission_classes = (IsManagement,)
