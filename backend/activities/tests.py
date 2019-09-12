from django.urls import reverse, path
from django.contrib.auth.models import Group

from rest_framework import status
from rest_framework.test import force_authenticate
from rest_framework.test import URLPatternsTestCase, APITestCase

from accounts.factories import UserFactory, AuthFactory

from activities.views import ColourThemeViewSet
from activities.factories import ColourThemeFactory


class ColourThemeTests(URLPatternsTestCase, APITestCase):
    urlpatterns = [
        path("colour/", ColourThemeViewSet.as_view({
            "post": "create", "get": "list",
        }), name="colour-theme-list"),

        path("colour/<int:pk>/", ColourThemeViewSet.as_view({
            "put": "update",
            "get": "retrieve",
            "patch": "partial_update",
            "delete": "destroy",
        }))
    ]

    fixtures = [
        "accounts/fixtures/groups.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.admin = UserFactory()
        cls.admin_auth = AuthFactory(user=cls.admin)

        cls.employer = UserFactory()
        cls.employer_auth = AuthFactory(user=cls.employer)

        cls.employee = UserFactory()
        cls.employee_auth = AuthFactory(user=cls.employee)

        admins = Group.objects.get(id=1)
        cls.admin.groups.add(admins)

        employers = Group.objects.get(id=2)
        cls.employer.groups.add(employers)

        employees = Group.objects.get(id=3)
        cls.employee.groups.add(employees)

    def test_admin_viewset_permissions(self):
        content = {
            "primary": 0x444444,
            "accent": 0x444444,
        }

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.admin_auth.plain}"
        )

        response = self.client.post(reverse("colour-theme-list"), content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        content["id"] = response.data["id"]
        response = self.client.get(reverse("colour-theme-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [content])
        self.assertDictEqual(response.data[0], content)

        response = self.client.get(
            reverse("colour-theme-detail", content["id"]),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, content)

        content = {**content, "primary": 0x555555}
        response = self.client.put(
            reverse("colour-theme-detail", content["id"]), content
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, content)


