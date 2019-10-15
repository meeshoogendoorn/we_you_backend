"""Models for storing information about remote activities."""

__all__ = (
    "Answer",
    "Answers",
    "Answered",

    "Session",
    "Question",
    "Reflection",
    "QuestionSet",
    "QuestionTheme",

)

from django.db.models import Model
from django.db.models.fields import TextField
from django.db.models.fields import CharField
from django.db.models.fields import DecimalField
from django.db.models.fields import DateTimeField
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields.related import CASCADE, ForeignKey
from django.db.models.fields.related import SET_NULL, ManyToManyField

from accounts.models import User
from companies.models import Company
from activities.utils import AnswerStyles


class QuestionTheme(Model):
    """
    The question theme.

    A question theme is the theme that will be used for
    a n number of question sets. This way if a certain
    theme is interesting it can be extended throughout
    multiple question sets.
    """
    label = CharField(max_length=255)


class AnswerStyle(Model):
    """
    A answer style.

    These records define the way a certain answer should be rendered,
    this way we can provide a better user experience by e.g. rendering
    a slide instead of radio buttons.
    """
    label = CharField(max_length=255, editable=False)


class QuestionSet(Model):
    """
    A question set for a single session.

    A question set is the collection of questions that will
    be questioned, and the result will only be used when all
    questions are answered.
    """
    label = CharField(max_length=255)
    theme = ManyToManyField(QuestionTheme, "sets")


class Session(Model):
    """
    A single session of questions for a theme.
    """
    class Meta:
        unique_together = ("company", "theme")

    set = ForeignKey(QuestionSet, CASCADE, "sessions")
    theme = ForeignKey(QuestionTheme, CASCADE, "sessions")

    start = DateTimeField()
    until = DateTimeField()

    company = ForeignKey(Company, "sessions")


class Answers(Model):
    """
    A collection of possible answers for a question.

    This model is mainly just a parent for the actual
    answers.
    """
    label = CharField(max_length=255, unique=True)
    style = ForeignKey(
        AnswerStyle, CASCADE, "styles", default=AnswerStyles.radio
    )


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


class Question(Model):
    """
    A single question to be answered.

    When the 'evaluate_employer' flag is set then there
    will be a notification that the employee wishes to
    evaluate with the employer.

    When the 'evaluate_administrator' flag is set then
    the user wishes to evaluate further with a employee
    of 'home4talent'.
    """

    class Meta:
        ordering = ("id",)

    set = ForeignKey(QuestionSet, CASCADE, "questions")
    weight = DecimalField(max_digits=3, decimal_places=2, default=1)
    deleted = DateTimeField(null=True)
    answers = ForeignKey(Answers, CASCADE, "questions")

    question = CharField(max_length=255, unique=True)


class Answered(Model):
    """
    The actual given answer of to a question of a user.

    This model defines the actual value of a user to a
    question by creating a reference to the value.

    A certain record of this model is considered property
    of a certain question session.
    """

    # TODO: fix bug in 'unique_together' ams nullable session
    class Meta:
        unique_together = ("answerer", "question", "session")
        order_with_respect_to = "question"

    value = DecimalField(max_digits=4, decimal_places=2)
    answer = ForeignKey(Answer, SET_NULL, "answered_questions", null=True)
    session = ForeignKey(Session, CASCADE, "answered_questions")

    answerer = ForeignKey(User, CASCADE, "answered_questions")
    question = ForeignKey(Question, SET_NULL, "answered_questions", null=True)


class AnsweredPlain(Model):
    """
    A open question answer (which is just plain text.

    This allows for open answers, but we aren't really sure what
    to do with it.
    """

    # TODO: fix bug in 'unique_together' ams nullable session
    class Meta:
        unique_together = ("answerer", "question", "session")
        order_with_respect_to = "question"

    value = TextField()
    session = ForeignKey(Session, CASCADE)

    answerer = ForeignKey(User, CASCADE)
    question = ForeignKey(Question, SET_NULL, null=True)


class Reflection(Model):
    """A additional reflection from a employee to QuestionGroup."""

    class Meta:
        unique_together = ("answerer", "question", "session")

    session = ForeignKey(Session, CASCADE, "reflections")
    answerer = ForeignKey(User, CASCADE, "reflections")
    question = ForeignKey(Question, CASCADE, "reflections")
    description = TextField()
