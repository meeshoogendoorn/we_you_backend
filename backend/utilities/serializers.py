import mimetypes

from drf_extra_fields.fields import Base64ImageField

from rest_framework.serializers import ModelSerializer, ChoiceField, CharField

from utilities.models import Image


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image

    path = CharField()
    mime = ChoiceField(choices={
        c for c in mimetypes.types_map.values() if c.startswith("image")
    })
    # Please note that this field sorts out more then
    # the allowed choices of the image type
    data = Base64ImageField()

