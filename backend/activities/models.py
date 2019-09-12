"""Models for storing information about remote activities."""

__all__ = (
    "Answer",
    "Question",
    "ColourTheme",
    "QuestionSet",
    "QuestionTheme",
)

from django.db.models import Model
from django.db.models.fields import BooleanField
from django.db.models.fields import BigIntegerField
from django.db.models.fields import TextField, CharField
from django.db.models.fields import PositiveSmallIntegerField

from django.db.models.fields.related import OneToOneField
from django.db.models.fields.related import CASCADE, ForeignKey

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator

from accounts.utils import is_employee
from accounts.models import User
from companies.models import Company


class ColourTheme(Model):
    """The storage for the colouring theme stored for a company."""
    company = OneToOneField(Company, CASCADE)

    primary = BigIntegerField(validators=[
        MinValueValidator(0x000000), MaxValueValidator(0xFFFFFFFF)]
    )

    accent = BigIntegerField(validators=[
        MinValueValidator(0x000000), MaxValueValidator(0xFFFFFFFF)]
    )

    # TODO: Add The logo


class QuestionTheme(Model):
    """
    The question theme.

    A question theme is the theme that will be used for
    a n number of question sets. This way if a certain
    theme is interesting it can be extended throughout
    multiple question sets.
    """
    company = ForeignKey(Company, CASCADE)

    # TODO: add timestamps of start and end?


class QuestionSet(Model):
    """
    A question set for a single session.

    A question set is the collection of questions that will
    be questioned, and the result will only be used when all
    questions are answered.
    """
    theme = ForeignKey(QuestionTheme, CASCADE)
    description = TextField()
    # TODO: add forward to employer or admin


class Question(Model):
    """A single question to be answered."""

    class Meta:
        ordering = ("id",)

    set = ForeignKey(QuestionSet, CASCADE)
    question = CharField(max_length=255)
    is_serious = BooleanField(default=True)


class Answer(Model):
    """The answer of a question linked to a user."""

    class Meta:
        unique_together = ("answerer", "question")
        order_with_respect_to = "question"

    rating = PositiveSmallIntegerField(validators=[
        MaxValueValidator(5), MinValueValidator(1)
    ])

    answerer = ForeignKey(User, CASCADE)
    question = ForeignKey(Question, CASCADE)

    # XXX MAYBE: remove and let it be handled by permission?
    def clean(self):
        """
        Make sure that the answerer is a employee.

        :raises ValidationError: When the user is not a employee
        """
        if is_employee(self.answerer):
            return

        raise ValidationError("A answer can only be answered by a employee")
