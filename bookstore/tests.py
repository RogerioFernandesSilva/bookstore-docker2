from django.test import TestCase


class SiteTestCase(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/bookstore/v1/product/")
        self.assertContains(response, "/api-token-auth/")

    def test_hello_page(self):
        response = self.client.get("/hello/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, World!")

    def test_api_still_requires_authentication(self):
        response = self.client.get("/bookstore/v1/product/")
        self.assertEqual(response.status_code, 401)
