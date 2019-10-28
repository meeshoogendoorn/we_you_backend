"""Company related models."""

__all__ = (
    "Member",
    "Company",
    "ColourTheme",
)

from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch.dispatcher import receiver

from django.db.models.base import Model
from django.db.models.signals import pre_delete

from django.db.models.fields import CharField
from django.db.models.fields import BigIntegerField
from django.db.models.fields.related import CASCADE, SET_NULL
from django.db.models.fields.related import OneToOneField, ForeignKey

from accounts.models import User
from utilities.models import Image


class Company(Model):
    """The main company model, exists mainly for the relations."""

    name = CharField(max_length=255)


class Member(Model):
    """Connects an accounts.User to a company."""

    company = ForeignKey(Company, CASCADE, "members")
    account = OneToOneField(User, CASCADE, related_name="member")


class ColourTheme(Model):
    """The storage for the colouring theme stored for a company."""

    company = OneToOneField(Company, CASCADE, related_name="theme")

    primary = BigIntegerField(validators=[
        MinValueValidator(0x000000), MaxValueValidator(0xFFFFFFFF)]
    )

    accent = BigIntegerField(validators=[
        MinValueValidator(0x000000), MaxValueValidator(0xFFFFFFFF)]
    )

    logo = ForeignKey(Image, SET_NULL, null=True)


@receiver(pre_delete, sender=Company)
def _cascade_delete_company(sender, instance, **kwargs):
    """
    Forward the deletion of a user account when the company is deleted.

    :param sender: The model's class
    :type sender: type of companies.models.Company

    :param instance: The company instance that was deleted
    :type instance: companies.models.Company

    :param kwargs: Additional keyword arguments
    :type kwargs: any
    """
    User.objects.filter(member__company=instance).delete()
    del sender, kwargs
