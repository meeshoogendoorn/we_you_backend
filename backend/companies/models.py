from django.db.models import Model
from django.db.models.fields import CharField


class Company(Model):
    name = CharField(max_length=255)
