from django.db.models import Model
from django.db.models.fields import CharField
from django.db.models.fields import DateTimeField
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import CASCADE, SET_NULL

from activities.models import Session
from accounts.models import User


class Answers(Model):
    """
    A collection of possible answers for a question.

    This model is mainly just a parent for the actual
    answers.
    """
    label = CharField(max_length=255, unique=True)


class Answer(Model):
    """
    A option of a answer collection.

    This model defines the actual value and label
    of a question.
    """

    class Meta:
        ordering = ("order",)
        unique_together = (("answers", "order"), ("answers", "label"))

    label = CharField(max_length=255)
    order = PositiveSmallIntegerField()

    answers = ForeignKey(Answers, CASCADE, "values")
    deleted = DateTimeField(null=True)


class Stimulation(Model):
    """
    A stimulation question to be answered.

    Question pops up after the default QuestionSet was finished.
    This question has fun facts and is more a game like idea.

    When a Stimulation question is linked to a Session he wil
    automatically will be used at the end of the Question session.
    """
    session = ForeignKey(Session, CASCADE, "stimulations")
    answers = ForeignKey(Answers, CASCADE, "stimulations")
    question = CharField(max_length=255, unique=True)


class Answered(Model):
    """
    The actual given answer of to a question of a user.

    This model defines the actual value of a user to a
    question by creating a reference to the value.

    A certain record of this model is considered property
    of a certain question session.
    """

    class Meta:
        unique_together = ("answerer", "question", "session")
        order_with_respect_to = "question"

    value = PositiveSmallIntegerField()
    answer = ForeignKey(Answer, SET_NULL, "answered_questions")
    session = ForeignKey(Session, CASCADE, "answered_questions")

    answerer = ForeignKey(User, CASCADE, "answered_questions")
    question = ForeignKey(Stimulation, CASCADE, "answered_questions")
