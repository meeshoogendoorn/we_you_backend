"""Utilities for the companies app."""

from accounts.utils import Groups
from accounts.models import Group
from accounts.factories import UserFactory

from companies.factories import MemberFactory
from companies.factories import CompanyFactory
from companies.factories import ColourThemeFactory

from analytics.models import MetaLink

def generate_company(employers=1, employees=15):  # pragma: no cover
    company = CompanyFactory()

    ColourThemeFactory(company=company)

    employer = Group.objects.get(id=Groups.employer)
    employee = Group.objects.get(id=Groups.employee)

    for i in range(0, employers):
        account = UserFactory(group=employer)
        MemberFactory(account=account, company=company)

    for i in range(0, employees):
        account = UserFactory(group=employee)
        MemberFactory(account=account, company=company)

    return company

def _generate_metadata(account)

def generate_environment(employer=1, employees=15):
    company = generate_company(employer, employees)

    meta_link = MetaLink.
