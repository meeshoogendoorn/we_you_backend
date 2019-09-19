"""Communication related models, will allow support for dynamic content."""

__all__ = (
    "Email",
    "Variable",
    "Environment",
)

from django.db.models import Model
from django.db.models.fields import TextField, CharField

from django.db.models.deletion import CASCADE
from django.db.models.deletion import PROTECT

from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField

from companies.models import Company

from communications.engine import EnvironmentEngine


class Variable(Model):
    """
    This model maintains the available variables.

    The values within this model are used to map human readable
    names within a piece of content to context.

    Context is a hard coded set of indexes with value's that are
    used to reformat the content. That's why the attribute can't
    be changed and that no additional records may be created or
    any deleted via a view. Only through a fixture.
    """
    name = CharField(max_length=255)
    attr = CharField(max_length=255, editable=False, unique=True)


class Environment(Model):
    """The environment stores which model instances are available."""

    label = CharField(max_length=255)
    variables = ManyToManyField(Variable)


class Email(Model):
    """
    Environment processable email.

    This model will be used within certain locations of this
    application to process emails based on variables available
    at that moment.

    The available variables are provided by the environment.

    If no email model for a specific company is proved, then the
    default email will be used where email is set to NULL.
    """

    class Meta:
        unique_together = ("environ", "company")

    content = TextField()
    subject = CharField(unique=True, max_length=78)
    environ = ForeignKey(Environment, PROTECT)
    company = ForeignKey(Company, CASCADE, null=True)

    def process_content(self, context):
        """
        Prepare the email for sending by filling in the variables.

        :param context: The current available variables
        :type context: dict

        :return: The processed email
        :rtype: str
        """
        engine = EnvironmentEngine(self.environ)
        return engine(self.content, context)
