"""Query generators for the analytics."""

__all__ = (
    "ValueCalculator",
)

from django.db.models.query import Q, F
from django.db.models.fields import DecimalField

from django.db.models.aggregates import Sum

from django.db.models.expressions import Func
from django.db.models.expressions import Value
from django.db.models.expressions import Subquery

from analytics.models import MetaData
from activities.models import Answered


class ValueCalculator(object):
    """
    Calculation query generator.

    Creates the calculation to process the value of a answered based on
    the currently authenticated user's meta data.
    """

    def __call__(self, user, data):
        """
        Create the query to calculate the value for a answered.

        :param user: The current user instance
        :type user: accounts.models.User

        :param data: The actual value of the answer
        :type data: decimal.decimal | float | int

        :return:
        """
        weight = self.calculate_weights(user)

        return Value(data) * weight

    def calculate_weights(self, user):
        """
        Calculate the weights of the users metadata.

        :param user: The current user instance
        :type user: accounts.models.User

        :return: A queryset with the average of the weights
        :rtype: django.db.models.query.QuerySet
        """
        query = MetaData.objects.filter(Q(usermeta__user=user.id))
        query = query.annotate(__result=Func("weight", function="AVG"))

        return query.values("__result")


class AnsweredCalculator(object):
    def __call__(self, question, company):
        clause = Q(session__company=company.id) & Q(question=question)
        notate = (
            Sum(F("question__weight") * F("value"))
            /
            Sum("question__weight")
        )

        queryset = Answered.objects.filter(clause)
        queryset = queryset.annotate(__result=notate)

        return queryset.value("__result")
