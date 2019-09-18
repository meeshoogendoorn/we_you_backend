"""Activity related serializers."""

__all__ = (
)

import datetime

from django.conf import settings
from django.core.mail import send_mass_mail
from django.db.models.query import Q

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from rest_framework.serializers import CurrentUserDefault
from knox.auth import TokenAuthentication
from utilities.fields import HyperlinkedRelatedReadField

from activities.models import Answer
from activities.models import Answers
from activities.models import Answered
from activities.models import Session
from activities.models import Question
from activities.models import Reflection
from activities.models import QuestionSet
from activities.models import QuestionTheme


from accounts.utils import Groups, is_employer
from accounts.models import User
from accounts.validators import GroupValidator

from companies.models import Company


class SessionSerializer(ModelSerializer):
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
    class Meta:
        model = Answered
        fields = ("id", "answerer", "answered", "question", "property")

    answerer = HyperlinkedRelatedReadField(
        queryset=User.objects.all(),
        view_name="",
        validators=[GroupValidator(Groups.employee)]
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
    )

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

    To create a reflection is optional.
    """

    class Meta:
        model = Reflection
        fields = ("id", "session", "answerer", "question", "description")

    session = HyperlinkedRelatedReadField(
        queryset=Session.objects.all(),
        view_name="",
    )

    question = HyperlinkedRelatedReadField(
        queryset=Question.objects.all(),
        view_name="",
    )

    answerer = HyperlinkedRelatedReadField(
        default=CurrentUserDefault(),
        view_name="",
        validators=[GroupValidator(Groups.employee)]
    )

    def save(self, **kwargs):
        """
        Overridden to inform management after storing the data.

        :param kwargs:

        :return:
        """
        instance = ModelSerializer.save(self, **kwargs)
        answerer = instance.answerer

        session = instance.session
        company = answerer.member.company

        # XXX TODO: refactor to assigned management member of some sorts?
        managers = User.objects.filter(groups=Groups.management)
        send_mass_mail(
            (
                f"Reflection of '{answerer.email}'",
                f"The user '{answerer.email}' of the company"
                f" {company.name}' wants to continue on the "
                f"question set {session.set.label} from the "
                f"theme {session.theme.label}."
                f"\n"
                f"\n"
                f"The user gave the following description: "
                f"\n"
                f"\n"
                f"{instance.description}",
                settings.DEFAULT_FROM_EMAIL,
                [manager.email]
            )
            for manager in managers
        )

        return instance

    def validate(self, attrs):
        session = attrs["session"]
        answerer = attrs["answerer"]
        question = attrs["question"]

        if not question.set.filter(sessions=session).exist():
            raise ValidationError # loose session

        if not question.answered_questions.filter(answerer=answerer).exists():
            raise ValidationError # invalid question answerer combi

        if not answerer.member.company.sessions.filter(session=session).exists():
            raise ValidationError # company doesn't own session

        return attrs
