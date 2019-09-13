"""Tests for the accounts app."""

import base64

from django.core import mail
from django.urls import reverse

from rest_framework import status
from rest_framework.test import URLPatternsTestCase, APITestCase

from accounts.urls import urlpatterns
from accounts.models import Group, User
from accounts.factories import UserFactory
from companies.factories import CompanyFactory


def basic_auth_header(username, password):
    """
    Create the value for the 'Authorization' HTTP header
    when using basic HTTP auth.

    :param username: The username of the user
    :type username: str

    :param password: The password of the user
    :type password: str

    :return: The value for the Authorization header with basic auth
    :rtype: str
    """
    credentials = f"{username}:{password}".encode("iso-8859-1")
    credentials = base64.b64encode(credentials).decode("iso-8859-1")

    return f"basic {credentials}"


def construct_headers(username, password):
    """
    Create a authorization header for basic authentication.

    :param username: The username of the user
    :type username: str

    :param password: The password of the user
    :type password: str

    :return: The authorization header as a kwarg
    :rtype: dict
    """
    return {
        "HTTP_AUTHORIZATION": basic_auth_header(username, password),
    }


class ViewSetIntegrationTests(URLPatternsTestCase, APITestCase):
    """Tests for account's view-sets."""

    urlpatterns = urlpatterns

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_successful_login(self):
        headers = construct_headers(self.user.email, "password")
        response = self.client.post(reverse("login"), **headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_unsuccessful_login(self):
        headers = construct_headers(self.user.email, "12345678")
        response = self.client.post(reverse("login"), **headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_create_employees(self):
        self.user.groups.add(Group.objects.get(id=2))

        company = CompanyFactory()
        members = ["user1@example.com", "user1@example.com"]
        content = {"company": company.id, "members": members}

        response = self.client.post(reverse("register-employees"), content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 2)

        self.user.groups.
