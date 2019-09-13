"""Factories for activity related models."""

import random

from factory import DjangoModelFactory, RelatedFactory, lazy_attribute

from companies.models import ColourTheme
from companies.factories import CompanyFactory


class ColourThemeFactory(DjangoModelFactory):
    """Factory for color theme's."""

    class Meta:
        model = ColourTheme

    company = RelatedFactory(CompanyFactory)

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
