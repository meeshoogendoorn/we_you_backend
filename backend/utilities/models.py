from django.db.models import Model
from django.db.models.fields import BinaryField, CharField


class Image(Model):
    mime = CharField(max_length=4)
    path = CharField(max_length=255)
    data = BinaryField()

