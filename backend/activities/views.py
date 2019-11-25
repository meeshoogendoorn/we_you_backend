"""Activity related views and view-sets."""

__all__ = (
    "AnswerViewSet",
    "AnswersViewSet",
    "SessionViewSet",
    "AnsweredViewSet",
    "QuestionViewSet",
    "ReflectionViewSet",
    "QuestionSetViewSet",
    "QuestionThemeViewSet",
)

import datetime

from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import RetrieveModelMixin

from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import GenericViewSet

from accounts.utils import is_management
from accounts.permissions import IsEmployeeOrReadOnly
from accounts.permissions import IsManagementOrReadOnly

from activities.models import Answer
from activities.models import Answers
from activities.models import Answered
from activities.models import Session
from activities.models import Question
from activities.models import Reflection
from activities.models import QuestionSet
from activities.models import QuestionTheme

from activities.serializers import AnswerSerializer
from activities.serializers import AnswersSerializer
from activities.serializers import SessionSerializer
from activities.serializers import QuestionSerializer
from activities.serializers import AnsweredSerializer
from activities.serializers import ReflectionSerializer
from activities.serializers import QuestionSetSerializer
from activities.serializers import QuestionThemeSerializer


class QuestionViewSet(ModelViewSet):
    """View-set for questions."""

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (IsManagementOrReadOnly,)


class QuestionSetViewSet(ModelViewSet):
    """View-set for question sets."""

    queryset = QuestionSet.objects.all()
    serializer_class = QuestionSetSerializer
    permission_classes = (IsManagementOrReadOnly,)


class AnswerViewSet(ModelViewSet):
    """
    View-set for answer records.

    This view-set will provide all answers, even when a answer was
    deleted so that it can retrieved easily for e.g. revival.
    """

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (IsManagementOrReadOnly,)

    def perform_destroy(self, instance):
        """
        Perform a soft delete instead of hard delete.

        This is done so that a answer can be used later for
        evaluation, even when the answer set was changed.

        :param instance: The instance to be deleted.
        :type instance: activities.models.Answer
        """
        instance.deleted = datetime.datetime.utcnow()
        instance.save()


class AnswersViewSet(ModelViewSet):
    """View-set for a answer set."""

    queryset = Answers.objects.all()
    serializer_class = AnswersSerializer
    permission_classes = (IsManagementOrReadOnly,)


class SessionViewSet(ModelViewSet):
    """View-set for question sessions."""

    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = (IsManagementOrReadOnly,)

    def filter_queryset(self, queryset):
        """
        Filter out the records related to other companies.

        :param queryset: The queryset to filter
        :type queryset: django.db.models.query.QuerySet

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        if is_management(self.request.user):
            return queryset

        company = self.request.user.member.company_id
        return queryset.filter(company=company)


class QuestionThemeViewSet(ModelViewSet):
    """View-set for question themes."""

    queryset = QuestionTheme.objects.all()
    serializer_class = QuestionThemeSerializer
    permission_classes = (IsManagementOrReadOnly,)


class AnsweredViewSet(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
):
    """View-set for answered questions."""

    queryset = Answered.objects.all()
    serializer_class = AnsweredSerializer
    permission_classes = (IsEmployeeOrReadOnly,)

    def filter_queryset(self, queryset):
        """
        Filter out the records related to other companies.

        :param queryset: The queryset to filter
        :type queryset: django.db.models.query.QuerySet

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        if is_management(self.request.user):
            return queryset

        company = self.request.user.member.company_id
        return queryset.filter(answerer__member__company=company)


class ReflectionViewSet(ModelViewSet):
    """View-set for reflections on questions."""

    queryset = Reflection.objects.all()
    serializer_class = ReflectionSerializer
    permission_classes = (IsEmployeeOrReadOnly,)

    def filter_queryset(self, queryset):
        """
        Filter out the records related to other companies.

        :param queryset: The queryset to filter
        :type queryset: django.db.models.query.QuerySet

        :return: The filtered queryset
        :rtype: django.db.models.query.QuerySet
        """
        if is_management(self.request.user):
            return queryset

        company = self.request.user.member.company_id
        return queryset.filter(answerer__member__company=company)
