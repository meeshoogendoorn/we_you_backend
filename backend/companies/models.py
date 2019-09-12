from django.db.models import Model
from django.db.models.fields import CharField
from django.db.models.fields.related import CASCADE, OneToOneField, ForeignKey
from accounts.models import User


class Company(Model):
    name = CharField(max_length=255)


class Member(Model):
    """Connects an accounts.User to a company."""
    company = OneToOneField(Company, CASCADE)
    account = ForeignKey(User, CASCADE, related_name="member")
