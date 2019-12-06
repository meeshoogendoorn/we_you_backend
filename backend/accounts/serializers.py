"""Account specific serializers."""

__all__ = (
    "AccountSerializer",
    "RegisterEmployerSerializer",
    "RegisterEmployeesSerializer",
)

from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.serializers import ListSerializer, Serializer
from rest_framework.serializers import ModelSerializer, EmailField

from accounts.utils import Groups
from accounts.models import Group, User
from companies.models import Company

from communications.utils import MultiMailTransport


class AccountSerializer(ModelSerializer):
    """Simple serializer for user model."""

    class Meta:
        model = User
        fields = ("id", "email", "group")


class RegisterEmployerSerializer(Serializer):
    """Create and register a new employer."""

    update = None
    create = None

    members = ListSerializer(child=EmailField())
    company = PrimaryKeyRelatedField(queryset=Company.objects.all())

    def save(self, **kwargs):
        """
        Register a new employer and notify him through email.

        :param kwargs: additional key word arguments (ignored)
        :type kwargs: any

        :return: The registered
        :rtype: accounts.models.User
        """
        group = Group.objects.get(id=Groups.employer)

        company = self.validated_data["company"]
        members = self.validated_data["members"]

        transport = MultiMailTransport({"company": company.name}, 2, company)

        seeder = (transport(*self.employ(a, company, group)) for a in members)
        return transport.finish(seeder)

    @staticmethod
    def employ(account, company, group):
        """
        Create and initialize a single employer.

        :param company: The company to employ the user for
        :type company: companies.models.Company

        :param account: The email address to create the account for
        :type account: str

        :param group: The group to assign the user to
        :type group: django.contrib.models.Group

        :return: The parameters to the transport
        :rtype: tuple
        """
        password = User.objects.make_random_password(12)
        instance = User.objects.create_user(email=account, password=password)
        receiver = instance.email

        instance.group = group
        instance.member.create(company=company)

        return receiver, {"email": receiver, "password": password}


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
        group = Group.objects.get(id=Groups.employee)

        company = self.validated_data["company"]
        members = self.validated_data["members"]

        transport = MultiMailTransport({"company": company.name}, 1, company)

        seeder = (transport(*self.employ(a, company, group)) for a in members)
        return transport.finish(seeder)

    @staticmethod
    def employ(account, company, group):
        """
        Create and initialize a single employee.

        :param company: The company to employ the user for
        :type company: companies.models.Company

        :param account: The email address to create the account for
        :type account: str

        :param group: The group to assign the user to
        :type group: django.contrib.models.Group

        :return: The parameters to the transport
        :rtype: tuple
        """
        password = User.objects.make_random_password(12)
        instance = User.objects.create_user(email=account, password=password)
        receiver = instance.email

        instance.group = group
        instance.member.create(company=company)

        return receiver, {"email": receiver, "password": password}
