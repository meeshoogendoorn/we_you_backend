"""Analytic related models, will provide the additional information."""

__all__ = (
    "MetaData",
    "MetaLink",
    "MetaType",
    "UserMeta",
)

from django.db.models import Model

from django.db.models.fields import CharField
from django.db.models.fields import DecimalField

from django.db.models.deletion import PROTECT, CASCADE, SET_NULL
from django.db.models.fields.related import OneToOneField, ForeignKey

from accounts.models import User
from companies.models import Company


class MetaLink(Model):
    """
    The link to the company.

    This is the root of the companies required meta data.
    The types related to this model will provide which meta data is
    required for a certain company.
    """

    company = OneToOneField(Company, CASCADE, related_name="metadata")


class MetaType(Model):
    """
    A meta data type.

    This is basically the category of a piece of meta data.
    It will provide the root of the options.
    """

    name = CharField(max_length=255, unique=True)
    link = ForeignKey(MetaLink, CASCADE, "types")


class MetaData(Model):
    """This model provide a type's option and the actual weight."""

    option = CharField(max_length=255)
    weight = DecimalField(default=1, max_digits=3, decimal_places=1)

    meta_type = ForeignKey(MetaType, CASCADE, "options")


class UserMeta(Model):
    """
    Loosely connected additional user information.

    This model will provide the relation between a meta option and a
    user. This way we can tell whether a certain weight must be added
    to the answer values of a user.
    """

    meta = ForeignKey(MetaData, PROTECT, "usermeta")
    user = ForeignKey(User, SET_NULL, "metadata", null=True)
