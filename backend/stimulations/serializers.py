"""Activity related serializers."""

__all__ = (
)

from rest_framework.serializers import IntegerField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CurrentUserDefault

from accounts.utils import Groups
from accounts.models import User
from accounts.validators import GroupValidator

from activities.models import Session
from activities.validators import SessionIsNowAlive
from activities.validators import SessionHasCompany

from stimulations.models import Answer
from stimulations.models import Answers
from stimulations.models import Stimulation
from stimulations.models import Answered

from utilities.fields import HyperlinkedRelatedReadField


class AnswerSerializer(ModelSerializer):
    """Serializer for a single answer."""

    class Meta:
        model = Answers
        fields = ("id", "label", "value", "answers")

    answers = HyperlinkedRelatedReadField(
        queryset=Stimulation.objects.all(),
        view_name="",
    )


class AnswersSerializer(ModelSerializer):
    """Serializer for a answer set."""

    class Meta:
        model = Answers
        fields = ("id", "label", "values")

    values = HyperlinkedRelatedReadField(
        queryset=Answer.objects.all(),
        view_name="",
    )


class StimulationSerializer(ModelSerializer):
    """Serializer for the stimulation question."""

    class Meta:
        model = Stimulation
        fields = ("id", "session", "answers", "question")


class AnsweredSerializer(ModelSerializer):
    """Serializer for a users 'answered': the answer to a question."""

    class Meta:
        model = Answered
        fields = ("id", "value", "label", "answerer", "question", "property")

    value = IntegerField(
        max_value=100,
        read_only=True,
    )

    answer = HyperlinkedRelatedReadField(
        queryset=Answer.objects.all(),
        view_name="",
    )

    session = HyperlinkedRelatedReadField(
        queryset=Session.objects.all(),
        view_name="",
        validators=[
            SessionHasCompany(),
            SessionIsNowAlive(),
        ]
    )

    answerer = HyperlinkedRelatedReadField(
        default=CurrentUserDefault(),
        queryset=User.objects.all(),
        view_name="",
        validators=[
            GroupValidator(Groups.employee),
        ]
    )

    question = HyperlinkedRelatedReadField(
        queryset=Stimulation.objects.all(),
        view_name="",
    )

