"""Company related models."""

from django.core.validators import MinValueValidator, MaxValueValidator

from django.db.models import Model, BigIntegerField
from django.db.models.fields import CharField
from django.db.models.fields.related import CASCADE, SET_NULL
from django.db.models.fields.related import OneToOneField, ForeignKey

from accounts.models import User
from utilities.models import Image


class Company(Model):
    """The main company model, exists mainly for the relations."""
    name = CharField(max_length=255)


class Member(Model):
    """Connects an accounts.User to a company."""
    company = OneToOneField(Company, CASCADE)
    account = ForeignKey(User, CASCADE, related_name="member")


class ColourTheme(Model):
    """The storage for the colouring theme stored for a company."""
    company = OneToOneField(Company, CASCADE)

    primary = BigIntegerField(validators=[
        MinValueValidator(0x000000), MaxValueValidator(0xFFFFFFFF)]
    )

    accent = BigIntegerField(validators=[
        MinValueValidator(0x000000), MaxValueValidator(0xFFFFFFFF)]
    )

    logo = ForeignKey(Image, SET_NULL, null=True)
