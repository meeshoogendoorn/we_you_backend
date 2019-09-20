"""Activity related serializers."""

__all__ = (
)

import datetime

from django.db.models.query import Q

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CurrentUserDefault

from utilities.fields import HyperlinkedRelatedReadField

from activities.models import Answer
from activities.models import Answers
from activities.models import Answered
from activities.models import Session
from activities.models import Question
from activities.models import Reflection
from activities.models import QuestionSet
from activities.models import QuestionTheme

from activities.validators import SessionIsNowAlive
from activities.validators import SessionHasCompany
from activities.validators import QuestionHasCompany
from activities.validators import QuestionIsAnswered

from accounts.utils import Groups, is_employer
from accounts.models import User
from accounts.validators import GroupValidator

from companies.models import Company
from communications.utils import MultiMailTransport


class SessionSerializer(ModelSerializer):
    """Serializer for a single session."""

    class Meta:
        model = Session
        fields = ("id", "set", "theme", "start", "until", "company")

    theme = HyperlinkedRelatedReadField(
        queryset=QuestionTheme.objects.all(),
        view_name="",
    )

    company = HyperlinkedRelatedReadField(
        queryset=Company.objects.all(),
        view_name="",
    )

    def validate(self, attrs):
        """
        Verify that a session is chronological and not in the past.

        :param attrs: The (by fields) validated values
        :type attrs: dict

        :return: The completely validated data
        :rtype: dict
        """
        if attrs["start"] >= attrs["until"]:
            raise ValidationError("Can not start after the end")

        if attrs["start"] < datetime.datetime.utcnow():
            raise ValidationError("Can not start in the past")

        return attrs


class QuestionThemeSerializer(ModelSerializer):
    """Serializer for the question theme."""

    class Meta:
        model = QuestionTheme
        fields = ("id", "label", "sets")

    sets = HyperlinkedRelatedReadField(
        many=True,
        queryset=QuestionSet.objects.all(),
        view_name="",
    )

    sessions = HyperlinkedRelatedReadField(
        many=True,
        queryset=Session.objects.all(),
        view_name="",
    )


class AnsweredSerializer(ModelSerializer):
    """Serializer for a users 'answered': the answer to a question."""

    class Meta:
        model = Answered
        fields = ("id", "answerer", "answered", "question", "property")

    answerer = HyperlinkedRelatedReadField(
        default=CurrentUserDefault(),
        queryset=User.objects.all(),
        view_name="",
        validators=[
            GroupValidator(Groups.employee),
        ]
    )

    answered = HyperlinkedRelatedReadField(
        queryset=Answer.objects.all(),
        view_name="",
    )

    question = HyperlinkedRelatedReadField(
        queryset=Question.objects.all(),
        view_name="",
    )

    property = HyperlinkedRelatedReadField(
        queryset=Session.objects.all(),
        view_name="",
        validators=[
            SessionHasCompany(),
            SessionIsNowAlive(),
        ]
    )

    def validate(self, attributes):
        """
        Validate the answer given and the additional context.

        Validates that the answered answer can be applied to the
        question, and that the question is actually found within
        the session's question set.

        :param attributes: The values to validate
        :type attributes: dict

        :return: The validated values
        :rtype: dict
        """
        clause = Q(answers__answer=attributes["answered"])
        clause = Q(id=attributes["question"]) & clause

        if not Question.objects.filter(clause).exists():
            raise ValidationError(
                "The given answer is not available to this question"
            )

        clause = Q(set__session=attributes["property"])
        clause = Q(id=attributes["question"]) & clause

        if not Question.objects.filter(clause).exists():
            raise ValidationError(
                "The question doesn't belong to this session"
            )

        return attributes

    def get_field_names(self, declared_fields, info):
        """
        Overridden to remove fields based on permissions.

        This method will remove the 'answerer' field from the
        serializer when the current user is a employee.

        This is because a employee may never know who gave
        answers except when the user created a reflection,
        but that's handled within the ReflectionSerializer.

        :param declared_fields: The declared fields of this serializer
        :type declared_fields: dict

        :param info: Additional info to be used

        :return: The names of the serializers to use
        :rtype: tuple
        """
        fields = ModelSerializer.get_field_names(self, declared_fields, info)

        if is_employer(self.context.request.user, False):
            del fields[fields.index("answerer")]

        return tuple(fields)


class ReflectionSerializer(ModelSerializer):
    """
    Serializer for the reflection of a user.

    This serializer handles a few ver strict and thorough validations
    because some of the fields are related through many-to-many fields
    and they MUST match for the data to make sense.
    """

    class Meta:
        model = Reflection
        fields = ("id", "session", "answerer", "question", "description")

    session = HyperlinkedRelatedReadField(
        queryset=Session.objects.all(),
        view_name="",
        validators=[
            SessionIsNowAlive(),
            SessionHasCompany(),
        ]
    )

    question = HyperlinkedRelatedReadField(
        queryset=Question.objects.all(),
        view_name="",
        validators=[
            QuestionIsAnswered(),
            QuestionHasCompany(),
        ]
    )

    answerer = HyperlinkedRelatedReadField(
        default=CurrentUserDefault(),
        read_only=True,
        view_name="account-detail",
        validators=[
            GroupValidator(Groups.employee),
        ]
    )

    def save(self, **kwargs):
        """
        Overridden to inform management after storing the data.

        :param kwargs: The additional data to save
        :type kwargs: any

        :return: The newly created reflection instance
        :rtype: activities.models.Reflection
        """
        # XXX TODO: refactor to assigned management member of some sorts?
        instance = ModelSerializer.save(self, **kwargs)
        managers = User.objects.filter(groups=Groups.management)

        context = self.get_context(instance)
        company = instance.answerer.member.company

        transport = MultiMailTransport(context, 3, company)
        transport.finish(transport(manager.email, {}) for manager in managers)

        return instance

    def validate(self, attributes):
        """
        Validate that the question has ties to the session.

        :param attributes: The values to validate
        :type attributes: dict

        :return: The validated values to create a reflection
        :rtype: dict
        """
        session = attributes["session"]
        question = attributes["question"]

        clause = Q(set__session=session.id) & Q(id=question.id)

        if Question.objects.filter(clause).exist():
            return attributes

        raise ValidationError(
            "The question doesn't have any ties to the session"
        )

    def get_context(self, instance):
        """
        Create the context to use for the email.

        :param instance: The current reflection instance
        :type instance: activities.models.Reflection

        :return: The created context
        :rtype: dict
        """
        return {
            "q_id": instance.question.id,
            "q_set": instance.session.set.label,
            "q_theme": instance.session.theme.label,
            "question": instance.question.question,

            "email": instance.answerer.email,
            "company": instance.answerer.member.company.name,
            "description": instance.description,
        }
