"""Unittests for the company app."""

from rest_framework import status

from rest_framework.test import APITestCase
from rest_framework.test import URLPatternsTestCase

from rest_framework.reverse import reverse
from rest_framework.request import Request

from accounts.utils import Groups
from accounts.models import Group

from accounts.factories import UserFactory
from accounts.factories import AuthFactory

from accounts.urls import urlpatterns as accounts_urlpatterns
from companies.urls import urlpatterns as company_urlpatterns

from companies.models import Member

from companies.factories import MemberFactory
from companies.factories import CompanyFactory


class TestCompanyView(URLPatternsTestCase, APITestCase):
    """Unittests for the CompanyView."""

    fixtures = ["groups"]
    urlpatterns = company_urlpatterns

    @classmethod
    def setUpTestData(cls):
        """
        Initialize the class by populating the database.

        Some notes:
          - The 'ignored' company is to make a clear difference in the
            response for management and members of a company.
        """

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
            reverse("member-detail", args=[member.id], request=request)
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
            args=[company.theme.id],
            request=request
        )


class TestMembersView(URLPatternsTestCase, APITestCase):
    """Unittests for the MemberViewSet."""

    fixtures = ["groups"]
    urlpatterns = accounts_urlpatterns + company_urlpatterns

    @classmethod
    def setUpTestData(cls):
        employer_group = Group.objects.get(id=Groups.employer)
        employee_group = Group.objects.get(id=Groups.employee)
        managing_group = Group.objects.get(id=Groups.management)

        cls.companyA = CompanyFactory()
        cls.companyB = CompanyFactory()

        cls.employerA = UserFactory(group=employer_group)
        cls.employeeA = UserFactory(group=employee_group)

        cls.employerB = UserFactory(group=employer_group)
        cls.employeeB = UserFactory(group=employee_group)

        cls.management = UserFactory(group=managing_group)

        cls.employee_a_token = AuthFactory(user=cls.employeeA)
        cls.employer_a_token = AuthFactory(user=cls.employerA)
        cls.employee_b_token = AuthFactory(user=cls.employeeB)
        cls.employer_b_token = AuthFactory(user=cls.employerB)
        cls.management_token = AuthFactory(user=cls.management)

        MemberFactory(account=cls.employerA, company=cls.companyA)
        MemberFactory(account=cls.employeeA, company=cls.companyA)
        MemberFactory(account=cls.employerB, company=cls.companyB)
        MemberFactory(account=cls.employeeB, company=cls.companyB)

    def test_list_members_as_employer(self):
        """Test the response of the member view as employer."""

        with self.subTest(user="employer A"):
            self._test_list_members_as_employer(
                self.employer_a_token.plain, self.companyA.members.all()
            )

        with self.subTest(user="employer B"):
            self._test_list_members_as_employer(
                self.employer_b_token.plain, self.companyB.members.all()
            )

    def _test_list_members_as_employer(self, token, members):
        """
        Actually test the members list as a employee.

        :param token: The authentication token to use
        :type token: str

        :param members: The members of the company
        :type members: django.db.models.query.QuerySet
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get(reverse("member-list"))

        request = Request(response.wsgi_request)
        members = [
            {
                "id": i,
                "account": reverse("account-detail", [a], None, request),
                "company": reverse("company-detail", [c], None, request),
            }

            for i, c, a in members.values_list("id", "company", "account")
        ]

        self.assertListEqual(members, response.data)

    def test_list_members_as_employee(self):
        """Test the response of the member view as employer."""

        with self.subTest(user="employee A"):
            self._test_list_members_as_employee(
                self.employee_a_token.plain,
                self.employeeA.member.id
            )

        with self.subTest(user="employee B"):
            self._test_list_members_as_employee(
                self.employee_b_token.plain,
                self.employeeB.member.id
            )

    def _test_list_members_as_employee(self, token, member):
        """
        Actually test the members list as a employee.

        :param token: The authentication token to use
        :type token: str

        :param members: The members of the company
        :type members: django.db.models.query.QuerySet
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get(reverse("member-list"))

        request = Request(response.wsgi_request)
        members = Member.objects.filter(id=member)
        members = [
            {
                "id": i,
                "account": reverse("account-detail", [a], None, request),
                "company": reverse("company-detail", [c], None, request),
            }

            for i, c, a in members.values_list("id", "company", "account")
        ]

        self.assertListEqual(members, response.data)

    def test_list_members_as_management(self):
        """Test the response of the member view as management."""

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.management_token.plain}"
        )

        response = self.client.get(reverse("member-list"))

        request = Request(response.wsgi_request)
        members = Member.objects.all()
        members = [
            {
                "id": i,
                "account": reverse("account-detail", [a], None, request),
                "company": reverse("company-detail", [c], None, request),
            }

            for i, c, a in members.values_list("id", "company", "account")
        ]

        self.assertListEqual(members, response.data)


class TestCompanyThemeView(URLPatternsTestCase, APITestCase):
    """Unittests for the Company Theme ViewSet."""

    fixtures = ["groups"]
    urlpatterns = company_urlpatterns

    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory()

        cls.employer = UserFactory(group=Group.objects.get(id=Groups.employer))
        cls.employee = UserFactory(group=Group.objects.get(id=Groups.employee))
        cls.managing = UserFactory(
            group=Group.objects.get(id=Groups.management)
        )

        cls.employee_token = AuthFactory(user=cls.employee)
        cls.employer_token = AuthFactory(user=cls.employer)
        cls.managing_token = AuthFactory(user=cls.managing)

        MemberFactory(account=cls.employer, company=cls.company)
        MemberFactory(account=cls.employee, company=cls.company)

    def test_list_colours_as_employee(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.employee_token.plain}"
        )

        response = self.client.get(reverse("colour-theme-list"))
        expected = [
            {
                "company": reverse(
                    "company-detail",
                    [self.company.id],
                    None,
                    Request(response.wsgi_request)
                ),

                "primary": self.company.theme.primary,
                "accent": self.company.theme.accent,
            }
        ]

        self.assertSequenceEqual(expected, response.data)
