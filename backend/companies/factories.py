"""Model factories for company related models."""

from factory import DjangoModelFactory, Faker

from companies.models import Company


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = Faker("company")
