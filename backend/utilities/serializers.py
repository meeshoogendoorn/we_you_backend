import base64
import mimetypes

from rest_framework.serializers import Field
from rest_framework.serializers import CharField
from rest_framework.serializers import ChoiceField
from rest_framework.serializers import ModelSerializer

from utilities.models import Image


class Base64Field(Field):
    """Simple serializer that will encode/decode raw data to base64."""

    def to_internal_value(self, data):
        return base64.b64decode(data)

    def to_representation(self, data):
        return base64.b64encode(data)


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "path", "mime", "data")

    path = CharField()
    mime = ChoiceField(choices={
        c for c in mimetypes.types_map.values() if c.startswith("image")
    })

    data = Base64Field()

