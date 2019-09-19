"""Custom managers for communication related models."""

__all__ = (
    "EmailManager",
)

from django.db.models.query import Q, F
from django.db.models.manager import Manager


class EmailManager(Manager):
    """Custom email manager to select the appropriate email."""

    def select_email(self, environ, company=None):
        """
        Select the appropriate email, with the default as fallback.

        :param environ: The environment to select for.
        :type environ: communications.models.Environment | int

        :param company: The company to prefer
        :type company: companies.models.Company | int | None

        :return: The appropriate email to use
        :rtype: communications.models.Email
        """
        queryset = self.get_queryset()
        queryset = queryset.order_by(F("company").desc(nulls_last=True))

        query = Q(environ=environ)

        if company is None:
            query &= Q(company__isnull=True)

        else:
            query &= Q(company__isnull=True) | Q(company=company)

        return queryset.filter(Q(company=company) | query).first()
