"""Model factories for company related models."""

__all__ = (
    "MemberFactory",
    "CompanyFactory",
    "ColourThemeFactory",
)

import random

from factory.faker import Faker
from factory.django import DjangoModelFactory
from factory.helpers import lazy_attribute
from factory.declarations import Iterator

from accounts.utils import Groups
from accounts.models import User

from companies.models import ColourTheme
from companies.models import Member, Company


class CompanyFactory(DjangoModelFactory):
    """Factory to generate companies."""

    class Meta:
        model = Company

    name = Faker("company")


class MemberFactory(DjangoModelFactory):
    """Factory to make a account a member."""

    class Meta:
        model = Member

    company = Iterator(Company.objects.all())
    account = Iterator(User.objects.filter(
        group__in=(Groups.employee, Groups.employer)
    ))


class ColourThemeFactory(DjangoModelFactory):
    """Factory for color themes."""

    class Meta:
        model = ColourTheme

    company = Iterator(CompanyFactory)

    @lazy_attribute
    def primary(self):
        """
        Generate a fake primary theme color.

        :return: The primary color of a theme
        :rtype: int
        """
        return random.randint(0x000000, 0xFFFFFF)

    @lazy_attribute
    def accent(self):
        """
        Generate a fake accent theme color.

        :return: The accent color of a theme
        :rtype: int
        """
        return random.randint(0x000000, 0xFFFFFF)
