"""Account specific serializers."""

__all__ = (
    "AccountSerializer",
    "RegisterEmployerSerializer",
    "RegisterEmployeesSerializer",
)

from django.conf import settings
from django.core.mail import send_mass_mail, send_mail

from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import ListSerializer, Serializer
from rest_framework.serializers import ModelSerializer, EmailField

from accounts.models import Group, User
from companies.models import Company, Member

from communications.models import Environment, Email


class AccountSerializer(ModelSerializer):
    """Simple serializer for user model."""

    class Meta:
        model = User
        fields = ("id", "email")


class RegisterEmployerSerializer(Serializer):
    """Create and register a new employer."""

    update = None
    create = None

    address = EmailField()
    company = PrimaryKeyRelatedField(queryset=Company.objects.all())

    def save(self, **kwargs):
        """
        Register a new employer and notify him through email.

        :param kwargs: additional key word arguments (ignored)
        :type kwargs: any

        :return: The registered
        :rtype: accounts.models.User
        """
        company = self.validated_data["company"]
        address = self.validated_data["address"]

        environ = Environment.objects.get(id=2)
        content = Email.objects.select_email(environ, company)

        password = User.objects.make_random_password(12)
        instance = User.objects.create_user(address, password)

        self.make_employer(company, instance)

        context = {
            "email": instance.email,
            "company": company.name,
            "password": password,
        }

        subject = content.subject
        content = content.process_content(context)

        send_mail(
            subject,
            content,
            settings.DEFAULT_FROM_EMAIL,
            (instance.email,)
        )

        return instance

    @staticmethod
    def make_employer(company, account):
        """
        Register the created user as a employer within his company.

        :param company: The company to register the user to
        :type company: companies.models.Company

        :param account: The user account to register
        :type account: accounts.models.User
        """
        Group.objects.get(id=3).users.add(account)
        Member.objects.create(company=company, account=account)


class RegisterEmployeesSerializer(Serializer):
    """Serializer to register a set of user's."""

    update = None
    create = None

    members = ListSerializer(child=EmailField())
    company = PrimaryKeyRelatedField(queryset=Company.objects.all())

    def save(self, **kwargs):
        """
        Create accounts for all the user's that are registered.

        :param kwargs: Additional creation kwargs (ignored)
        :type kwargs: any

        :return: The number of send emails
        :rtype: int
        """

        company = self.validated_data["company"]
        environ = Environment.objects.get(id=1)
        content = Email.objects.select_email(environ, company)

        members = self.validated_data["members"]
        factory = self.factory(company, content)

        return send_mass_mail(tuple(map(factory, members)))

    def factory(self, company, content):
        """
        Create a callback for user creation.

        :param company: The company of the employee
        :type company: companies.models.Company

        :param content: The email model that contains the content
        :type content: communications.models.Email

        :return: The actual factory: a callback that creates the account
        :rtype: callable
        """
        context = {"company": company.name}

        def _factory(account):
            instance, password = self.create_user(account)

            self.employ_user(instance, company)

            return self.inform_user(instance, password, content, context)

        return _factory

    @staticmethod
    def inform_user(instance, password, content, context):
        """
        Prepare a single message to be send to a employee.

        :param instance: The user model of the employee
        :type instance: accounts.models.User

        :param password: The generated password
        :type password: str

        :param content: The email to use as content

        :param context: The context to process the content
        :type context: dict

        :return: A tuple with the content to send
        :rtype: tuple
        """
        context = {**context, "email": instance.email, "password": password}

        return (
            content.subject, content.process_content(context),
            settings.DEFAULT_FROM_EMAIL, (instance.email,)
        )

    @staticmethod
    def create_user(account):
        """
        Create and initialize a single employee.

        :param company:

        :param account:

        :return:
        """
        password = User.objects.make_random_password(12)
        instance = User.objects.create_user(email=account, password=password)

        return instance, password

    @staticmethod
    def employ_user(account, company):
        """
        Add the user to the employee's group

        :param account: The user instance
        :type account: accounts.models.User

        :param company: The company of the employee
        :type company: companies.models.Company
        """
        Group.objects.get(id=3).users.add(account)
        Member.objects.create(company=company, account=account)
