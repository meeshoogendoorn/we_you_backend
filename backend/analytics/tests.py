
from rest_framework.test import APITestCase

from activities.models import *
from companies.factories import *

class CompanyChartTest(APITestCase):
    def test_all(self):
