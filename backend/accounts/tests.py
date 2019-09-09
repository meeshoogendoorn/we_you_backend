"""Tests for the accounts app."""

import base64

from django.urls import reverse, path

from rest_framework import status
from rest_framework.test import URLPatternsTestCase, APITestCase

from accounts.views import LoginView
from accounts.factories import UserFactory


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

    urlpatterns = [
        path("/login/", LoginView.as_view(), name="login"),
    ]

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_successful_login(self):
        headers = construct_headers(self.user.username, "password")
        response = self.client.post(reverse("login"), **headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_unsuccessful_login(self):
        headers = construct_headers(self.user.username, "12345678")
        response = self.client.post(reverse("login"), **headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
