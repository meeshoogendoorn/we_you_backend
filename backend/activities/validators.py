"""Custom validators for activities and relations."""

__all__ = (
    "SessionIsNowAlive",
    "SessionHasCompany",
    "QuestionHasCompany",
    "QuestionIsAnswered",
)

import datetime

from django.db.models.query import Q

from rest_framework.exceptions import ValidationError

from activities.models import Question, Session


class SessionIsNowAlive(object):
    """Check is a session is currently alive."""

    def __call__(self, session):
        """
        Validate that the current time is within the session's lifetime.

        :param session: The session to verify
        :type session: activities.models.Session

        :return: The validated session
        :rtype: activities.models.Session
        """
        moment = datetime.datetime.utcnow()
        clause = Q(start__lte=moment) & Q(until_gte=moment)

        if Session.objects.filter(clause).exists():
            return session

        raise ValidationError("The session is not alive at this moment")


class SessionHasCompany(object):
    """Check if a related session that is tried to be set is still valid."""

    def __call__(self, session):
        """
        Validate that the user's company has a certain session.

        :param session: The session to verify
        :type session: activities.models.Session

        :return: The validated session
        :rtype: activities.models.Session
        """
        member = getattr(self, "member")
        clause = Q(company__member__account=member)
        clause = Q(id=session.id) & clause

        if Session.objects.filter(clause).exists():
            return session

        raise ValidationError("The users company doesn't own this session")

    def set_context(self, serializer):
        """
        Extract the current authenticated user from the request.

        :param serializer: The currently active serializer field
        :type serializer: rest_framework.serializers.Field
        """
        setattr(self, "member", serializer.context.request.user)


class QuestionHasCompany(object):
    """
    Check if a related question belongs to the company of the user."""

    def __call__(self, question):
        """
        Validate that the user's company has ties to the answer.

        :param question: The question to verify
        :type question: activities.models.Question

        :return: The validated session
        :rtype: activities.models.Session
        """
        member = getattr(self, "member")
        clause = Q(set__session__company__member__account=member)
        clause = Q(id=question.id) & clause

        if Question.objects.filter(clause).exists():
            return question

        raise ValidationError(
            "The users company doesn't have any ties to this question"
        )

    def set_context(self, serializer):
        """
        Extract the current authenticated user from the request.

        :param serializer: The currently active serializer field
        :type serializer: rest_framework.serializers.Field
        """
        setattr(self, "member", serializer.context.request.user)


class QuestionIsAnswered(object):
    """Check if the current user answered the question."""

    def __call__(self, question):
        """
        Validate that the current user answered the question.

        :param question: The question to validate
        :type question: activities.models.Question

        :return: The validated question
        :rtype: activities.models.Question
        """

        clause = Q(answered__answerer=getattr(self, "answerer"))
        clause = clause & Q(id=question.id)

        if Question.objects.filter(clause).exist():
            return question

        raise ValidationError(
            "The question wasn't answered by the user"
        )

    def set_context(self, serializer):
        """
        Extract the current authenticated user from the request.

        :param serializer: The currently active serializer field
        :type serializer: rest_framework.serializers.Field
        """
        setattr(self, "answerer", serializer.context.request.user)
