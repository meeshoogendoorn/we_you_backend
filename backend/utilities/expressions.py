"""Custom SQL expressions for general purpose."""

__all__ = (
    "Count",
)

import abc

from django.db.models.fields import IntegerField
from django.db.models.expressions import Star, Func


class Count(abc.ABC, Func):
    """
    Custom SQL `COUNT` function without `GROUP BY`.

    This SQL `COUNT` directly inherits from Func() instead of Aggregate
    like django's default COUNT function. This way the `GROUP BY` order
    isn't added.
    """

    name = "Count"
    function = "COUNT"

    output_field = IntegerField()
    allow_distinct = True

    def __init__(self, expression, **extra):
        """
        Overridden to check for filtering star expressions.

        :param expression: The SQL function expression
        :type expression: django.db.models.expressions.Expression | str

        :param extra: Additional keyword arguments to pass on
        :type extra: any
        """
        expression = Star() if expression == "*" else expression
        has_filter = "filter" in extra and extra["filter"] is not None

        if isinstance(expression, Star) and has_filter:
            raise ValueError("Star cannot be used with filter.")

        Func.__init__(self, expression, filter=filter, **extra)

    def convert_value(self, value, expression, connection):
        """
        Sanitize NULL value's.

        :param value: The value to sanitize
        :type value: int | None

        :param expression: The currently used function expression
        :type expression: django.db.models.expressions.Expression

        :param connection: The current connection proxy
        :type connection: django.db.DefaultConnectionProxy
        """
        return 0 if value is None else value
