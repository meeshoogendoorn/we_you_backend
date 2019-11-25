"""ViewSets for the analytics app."""

from django.db.models.query import F
from django.db.models.fields import DecimalField

from django.db.models.expressions import OuterRef, Case
from django.db.models.expressions import Subquery, When
from django.db.models.expressions import ExpressionWrapper

from django.db.models.functions import Now
from django.db.models.aggregates import Avg, Sum

from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from analytics.serializers import CompanyChartSerializer

from companies.models import Company
from activities.models import Session


class CompanyChartsViewSet(GenericViewSet, ListModelMixin):
    queryset = Company.objects.annotate(
        __session_average=Subquery(
            Session.objects.filter(
                company=OuterRef("id")
            ).annotate(
                value=ExpressionWrapper(
                    Avg("answered_questions__value")
                    *
                    F("set__weight"),
                    output_field=DecimalField(
                        max_digits=3,
                        decimal_places=2,
                    )
                )
            ).values("value")
        )
    ).annotate(
        date=Case(
            When(
                sessions__until__lte=Now(),
                then=F("sessions__until")
            ),
            default=Now()
        ),
        data=ExpressionWrapper(
            Sum("__session_average")
            *
            F("sessions__theme__weight"),

            output_field=DecimalField(decimal_places=2, max_digits=3)
        )
    ).values("data", "date")

    serializer_class = CompanyChartSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(id=self.request.user.member.company_id)


class SessionChartsViewSet(GenericViewSet, ListModelMixin):
    queryset = Session.objects.annotate(
        data=Avg("answered_questions__value") * F("set__weight"),
        date=Case(
            When(until__lte=Now(), then=F("until")),
            default=Now()
        ),
    )

    def filter_queryset(self, queryset):
        return queryset.filter(id=self.request.user.member.company_id)
