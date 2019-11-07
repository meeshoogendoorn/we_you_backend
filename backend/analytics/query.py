"""Query generators for the analytics."""

__all__ = (
    "get_value_query",
    "add_session_calculations",
)

from django.db.models.query import Q, F
from django.db.models.fields import DecimalField

from django.db.models.aggregates import Avg

from django.db.models.expressions import Func
from django.db.models.expressions import Value
from django.db.models.expressions import Subquery

from analytics.models import MetaData


def _calculate_value_weights(user, question):
    """
    Calculate the weights of the users metadata.

    :param user: The current user instance
    :type user: accounts.models.User

    :type question: The question that is answered
    :type question: activities.models.Question

    :return: A queryset with the average of the weights
    :rtype: django.db.models.query.QuerySet
    """
    model = question.__class__
    sub_q = model.objects.filter(id=question.id)
    sub_q = sub_q.value("weight")

    query = MetaData.objects.filter(Q(usermeta__user=user.id))
    query = query.values("weight").union(sub_q)
    query = query.annotate(__result=Func("weight", function="AVG"))

    return query.values("__result")


def get_value_query(user, data, question):
    """
    Get the query to calculate the value of a answered value.

    :param user: The current user instance
    :type user: accounts.models.User

    :param data: The actual submitted value
    :type data: int

    :type question: The question that is answered
    :type question: activities.models.Question

    :return: The query to calculate the value.
    :rtype: django.db.models.query.QuerySet
    """
    weight = _calculate_value_weights(user, question)

    return Value(data) * weight


# XXX TODO: remove
def add_session_calculations(queryset):
    """

    :param queryset:
    :return:
    """
    query = Avg("answered_questions__value") * F("set__weight")
    return queryset.annotate(value=query)

