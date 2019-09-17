"""Account specific serializers."""

__all__ = (
    "AccountSerializer",
    "RegisterEmployerSerializer",
    "RegisterEmployeesSerializer",
)

from django.conf import settings
from django.core.mail import send_mass_mail

from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import ListSerializer, Serializer
from rest_framework.serializers import ModelSerializer, EmailField

from accounts.models import Group, User
from companies.models import Company, Member


class AccountSerializer(ModelSerializer):
    """Simple serializer for user model."""

    class Meta:
        model = User
        fields = ("id", "email")


class RegisterEmployerSerializer(Serializer):
    update = None
    create = None

    address = EmailField()
    company = PrimaryKeyRelatedField(queryset=Company.objects.all())

    def save(self, **kwargs):
        company = self.validated_data["company"]
        address = self.validated_data["address"]

        password = User.objects.make_random_password(12)
        instance = User.objects.create_user(address, password)

        self.make_employer(company, instance)

        return instance

    @staticmethod
    def make_employer(company, account):
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
        pending = []
        company = self.validated_data["company"]

        for account in self.validated_data["members"]:
            instance, password = self.create_user(account)

            self.employ_user(instance, company)
            pending.append(self.inform_user(instance, password))

        return send_mass_mail(pending)

    @staticmethod
    def inform_user(instance, password):
        """
        Prepare a single message to be send to a employee.

        :param instance: The user model of the employee
        :type instance: accounts.models.User

        :param password: The generated password
        :type password: str

        :return: A tuple with the content to send
        :rtype: tuple
        """
        return (
            f"New we you account created for {instance.email}",
            f"""
            A new user account is We You account is created for you:
                email: {instance.email}
                password: {password}
            """,
            settings.DEFAULT_FROM_EMAIL,
            (instance.email,)
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
