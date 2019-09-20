"""Account specific serializers."""

__all__ = (
    "AccountSerializer",
    "RegisterEmployerSerializer",
    "RegisterEmployeesSerializer",
)

from django.conf import settings
from django.core.mail import send_mail

from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import ListSerializer, Serializer
from rest_framework.serializers import ModelSerializer, EmailField

from accounts.models import User
from companies.models import Company

from communications.utils import MultiMailTransport
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
        handler = Email.objects.select_email(environ, company)

        password = User.objects.make_random_password(12)
        instance = User.objects.create_user(address, password)

        instance.group = 3
        instance.member.create(company=company)

        context = {
            "email": address,
            "company": company.name,
            "password": password,
        }

        subject = handler.subject
        content = handler.process_content(context)

        send_mail(
            subject, content,
            settings.DEFAULT_FROM_EMAIL, [address]
        )

        return instance


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
        members = self.validated_data["members"]

        transport = MultiMailTransport({"company": company.name}, 1, company)

        seeder = (transport(*self.employ(a, company)) for a in members)
        return transport.finish(seeder)

    @staticmethod
    def employ(account, company):
        """
        Create and initialize a single employee.

        :param company: The company to employ the user for
        :type company: companies.models.Company

        :param account: The email address to create the account for
        :type account: str

        :return: The parameters to the transport
        :rtype: tuple
        """
        password = User.objects.make_random_password(12)
        instance = User.objects.create_user(email=account, password=password)
        receiver = instance.email

        instance.group = 3
        instance.member.create(company=company)

        return receiver, {"email": receiver, "password": password}
