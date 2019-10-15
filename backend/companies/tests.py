from rest_framework import status

from rest_framework.test import APITestCase
from rest_framework.test import URLPatternsTestCase

from rest_framework.reverse import reverse
from rest_framework.request import Request

from accounts.utils import Groups
from accounts.models import Group
from accounts.factories import UserFactory
from accounts.factories import AuthFactory

from companies.urls import urlpatterns
from companies.factories import MemberFactory
from companies.factories import CompanyFactory


class TestCompanyView(URLPatternsTestCase, APITestCase):

    fixtures = ["groups"]
    urlpatterns = urlpatterns

    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory()
        cls.ignored = CompanyFactory()

        cls.external = UserFactory(group=Group.objects.create(name="external"))
        cls.employer = UserFactory(group=Group.objects.get(id=Groups.employer))
        cls.employee = UserFactory(group=Group.objects.get(id=Groups.employee))

        cls.external_token = AuthFactory(user=cls.external)
        cls.employer_token = AuthFactory(user=cls.employer)
        cls.employee_token = AuthFactory(user=cls.employee)

        MemberFactory(account=cls.employer, company=cls.company)
        MemberFactory(account=cls.employee, company=cls.company)

        cls.management = UserFactory(
            group=Group.objects.get(id=Groups.management)
        )

        cls.administrator = UserFactory(
            group=Group.objects.get(id=Groups.admin)
        )

        cls.management_token = AuthFactory(user=cls.management)
        cls.administrator_token = AuthFactory(user=cls.administrator)

    def test_authorization(self):
        """Verify that authorization is required."""

        self.client.credentials()

        response = self.client.get(reverse("company-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_acceptable_permissions(self):
        """Verify that authorization is required."""

        authorization = f"Token {self.external_token.plain}"
        self.client.credentials(HTTP_AUTHORIZATION=authorization)

        response = self.client.get(reverse("company-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_companies_as_member(self):
        """Validate the response from the company view for the employee."""

        with self.subTest(group="employee"):
            authorization = self.employee_token.plain
            self._test_list_companies_as_member(authorization, False)

        with self.subTest(group="employer"):
            authorization = self.employer_token.plain
            self._test_list_companies_as_member(authorization, True)

    def _test_list_companies_as_member(self, token, include_members):
        """
        The actual test for the company overview through members.

        This function is used as a sub-test for
        'test_list_companies_as_member' to avoid code repetition.

        :param token: The authorization token to include
        :type token: str

        :param include_members: tells to include the members or not
        :type include_members: bool
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get(reverse("company-list"))

        request = Request(response.wsgi_request)
        content = {
            "id": self.company.id,
            "name": self.company.name,
            "theme": self._reverse_colour_theme(self.company, request),
        }

        if include_members:
            members = self.company.members.all()
            members = self._reverse_memberships(members, request)

            content["members"] = members

        self.assertIsInstance(response.data, list)

        self.assertEqual(len(response.data), 1)
        self.assertDictEqual(response.data[0], content)

    def test_list_companies_as_management(self):
        """Validate the response for the management."""

        with self.subTest(group="admin"):
            authorization = self.administrator_token.plain
            self._test_list_companies_as_management(authorization)

        with self.subTest(group="management"):
            authorization = self.management_token.plain
            self._test_list_companies_as_management(authorization)

    def _test_list_companies_as_management(self, token):
        """
        The actual test for the company overview through management.

        :param token: The authorization token to include
        :type token: str
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get(reverse("company-list"))

        request = Request(response.wsgi_request)
        members = self.company.members.all()
        members = self._reverse_memberships(members, request)

        company = {
            "id": self.company.id,
            "name": self.company.name,
            "theme": self._reverse_colour_theme(self.company, request),
            "members": members
        }

        ignored = {
            "id": self.ignored.id,
            "name": self.ignored.name,
            "theme": self._reverse_colour_theme(self.ignored, request),
            "members": [],
        }

        self.assertIsInstance(response.data, list)

        self.assertEqual(len(response.data), 2)
        self.assertDictEqual(response.data[0], company)
        self.assertDictEqual(response.data[1], ignored)

    def _reverse_memberships(self, members, request):
        """
        Retrieve the complete URI's for each member.

        :param members: The queryset with the members
        :type members: django.db.models.query.QuerySet

        :param request: The request to retrieve the domain from
        :type request: rest_framework.request.Request

        :return: The retrieved URI's of the memberships
        :rtype: list
        """
        return [
            reverse("member-detail", args=(member.id,), request=request)
            for member in members
        ]

    def _reverse_colour_theme(self, company, request):
        """
        Retrieve the complete URI for the companies theme.

        :param company: The company who's theme to retrieve.
        :type company: companies.models.Company

        :param request: The request instance that holds the domain
        :type request: rest_framework.request.Request

        :return: The complete URI
        :rtype: str
        """
        return reverse(
            "colour-theme-detail",
            args=(company.theme.id,),
            request=request
        )
