"""Activity related serializers."""

__all__ = (
    "AnswerSerializer",
    "AnswersSerializer",
    "SessionSerializer",
    "AnsweredSerializer",
    "QuestionSerializer",
    "ReflectionSerializer",
    "QuestionSetSerializer",
    "QuestionThemeSerializer",
)

import datetime

from django.db.models.query import Q
from django.db.models.expressions import Subquery, Value

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import IntegerField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CurrentUserDefault

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

from accounts.utils import Groups, is_employee
from accounts.models import User
from accounts.validators import GroupValidator

from companies.models import Company
from communications.utils import MultiMailTransport

from utilities.fields import HyperlinkedRelatedReadField
from utilities.expressions import Count


class QuestionSerializer(ModelSerializer):
    """Serializer for a single question."""

    class Meta:
        model = Question
        fields = ("id", "set", "answers", "question")

    set = HyperlinkedRelatedReadField(
        queryset=QuestionSet.objects.all(),
        view_name=""
    )

    answers = HyperlinkedRelatedReadField(
        queryset=Answers.objects.all(),
        view_name=""
    )


class QuestionSetSerializer(ModelSerializer):
    """Serializer for question sets."""

    class Meta:
        model = QuestionSet
        fields = ("id", "label", "theme")

    theme = HyperlinkedRelatedReadField(
        queryset=QuestionTheme.objects.all(),
        view_name="",
    )


class AnswerSerializer(ModelSerializer):
    """Serializer for a single answer."""

    class Meta:
        model = Answer
        fields = ("id", "label", "order", "answers")


class AnswersSerializer(ModelSerializer):
    """Serializer for a answer set."""

    class Meta:
        model = Answers
        fields = ("id", "label", "values")

    values = HyperlinkedRelatedReadField(
        queryset=Answer.objects.filter(deleted__isnull=True),
        view_name="",
    )


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


class _TimeAwareHyperlinkField(HyperlinkedRelatedReadField):
    """Special related field for relations towards active sessions."""

    def get_queryset(self):
        """
        Filter out the sessions that already have past.

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        return self.queryset.filter(until__gte=datetime.datetime.utcnow())


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

    sessions = _TimeAwareHyperlinkField(
        many=True,
        queryset=Session.objects.all(),
        view_name="",
    )


class AnsweredSerializer(ModelSerializer):
    """Serializer for a users 'answered': the answer to a question."""

    class Meta:
        model = Answered
        fields = ("id", "value", "label", "session", "answerer", "question")
        extra_kwargs = {"answerer": {"write_only": True}}

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
        queryset=Question.objects.all(),
        view_name="",
    )

    def save(self, **kwargs):
        """
        Overridden to add the copy-query to the value.

        The value and actual answer are copied in case that the answer
        set (Answers) is changed. This way we can maintain the actual
        value and delete the answer, or change it, safely and maintain
        data integrity.

        :param kwargs: The additional data to add to validated_data
        :type kwargs: any

        :return: The newly created 'Answered' instance
        :rtype: activities.models.Answered
        """
        if "value" not in kwargs:
            kwargs["value"] = self.get_calculation(
                self.validated_data["answer"]
            )

        return ModelSerializer.save(self, **kwargs)

    def get_relative_value(self, answer):
        """
        Get the value of the answer relative to his siblings.

        This is a value from 1 to n where n is the number of
        siblings. The actual value will be calculated as:

        v = ceil((100 / e) * n)

        where
            n = The position of the given answer relative to the
                other answers.
            e = The number of answers within a answer set
            v = The actual value
        """
        queryset = Answers.objects.filter(values=answer)[:1]
        queryset = Answer.objects.filter(
            answers=queryset, deleted__isnull=True
        )

        queryset = queryset.order_by("order")
        queryset = queryset.filter(order__lte=answer.order)

        queryset = queryset.annotate(__index=Count("*"))
        queryset = queryset.values("__index")

        return Subquery(queryset)

    def get_sibling_answers(self, answer):
        """
        Get all 'sibling answers' from a answer though nested query.
        """
        queryset = Answers.objects.filter(values=answer)[:1]
        queryset = Answer.objects.filter(
            answers=queryset, deleted__isnull=True
        )

        return queryset

    def set_annotation(self, queryset):
        """
        Set the annotation on the (to be) subquery.
        """
        queryset = queryset.order_by()
        queryset = queryset.annotate(__count=Count("*"))
        queryset = queryset.values("__count")

        return queryset

    def get_calculation(self, answer):
        """
        Finalize the value by creating the calculation.
        """
        relative = self.get_relative_value(answer)
        queryset = self.get_sibling_answers(answer)
        queryset = self.set_annotation(queryset)

        return (Value(100) / Subquery(queryset)) * relative

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

    def get_extra_kwargs(self):
        """
        Overridden to hide the answerer for management or employer.

        This is because a employee may never know who gave answers
        except when the user created a reflection, but that's handled
        within the ReflectionSerializer.

        :return: The extra keyword arguments for the fields
        :rtype: dict
        """
        extra = ModelSerializer.get_extra_kwargs(self)

        if is_employee(self.context.request.user):
            current_arguments = extra.get(extra["answerer"], {})
            extra["answerer"] = {**current_arguments, "write_only": False}

        return extra


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
