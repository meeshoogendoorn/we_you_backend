"""Model factories for the analytics app."""

import random

from factory import Faker
from factory.django import DjangoModelFactory
from factory.helpers import lazy_attribute

from factory.declarations import Iterator
from factory.declarations import RelatedFactory
from factory.declarations import RelatedFactoryList

from accounts.utils import Groups
from accounts.models import Group
from accounts.factories import UserFactory

from companies.factories import MemberFactory
from companies.factories import CompanyFactory

from analytics.models import MetaLink
from analytics.models import MetaData
from analytics.models import MetaType
from analytics.models import UserMeta


class _MetaDataFactory(DjangoModelFactory):
    option = Faker("job")

    meta_type = Iterator(MetaType.objects.all())

    @lazy_attribute
    def weight(self):
        return random.randint(0, 10) / 10


class _MetaTypeFactory(DjangoModelFactory):
    """

    """

    class Meta:
        model = MetaType

    name = Faker("job")

    options = RelatedFactoryList(_MetaDataFactory, "link", size=5)


class _UserMetaFactory(DjangoModelFactory):
    class Meta:
        model = UserMeta

    meta = RelatedFactory(_MetaDataFactory)
    user = RelatedFactory(UserFactory)


class _MetaLinkFactory(DjangoModelFactory):
    """
    Factory for a Meta Link.
    """

    class Meta:
        model = MetaLink

    company = RelatedFactory(CompanyFactory)


class _UserFactory(UserFactory):
    group = Iterator(Group.objects.filter(id__in=[
        Groups.employer,
        Groups.employee,
    ]))
    metadata = RelatedFactoryList(_UserMetaFactory, "user", size=2)


class _MemberFactory(MemberFactory):
    account = RelatedFactory(_UserFactory)


class CompleteCompanyFactory(CompanyFactory):
    link = RelatedFactory(_MetaLinkFactory, "company")
    members = RelatedFactoryList(_MemberFactory, "company", size=30)
