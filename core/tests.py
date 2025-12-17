from django.test import TestCase
from django.urls import reverse


class CoreSmokeTests(TestCase):
    def test_homepage_has_auth_links(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounts:login"))
        self.assertContains(response, reverse("accounts:register"))

    def test_health_endpoint_returns_status(self):
        response = self.client.get(reverse("core:health"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("status", payload)
        self.assertIn("db_ok", payload)

