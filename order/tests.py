from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from order.models import Order
from product.models import Product


class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tester", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        self.token = Token.objects.create(user=self.user)
        self.p1 = Product.objects.create(title="Livro A", price=100)
        self.p2 = Product.objects.create(title="Livro B", price=50)
        self.url = "/bookstore/v1/order/"

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_calculates_total(self):
        self.auth()
        payload = {"products_id": [self.p1.id, self.p2.id]}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total"], 150)
        self.assertEqual(response.data["user"], "tester")
        self.assertEqual(Order.objects.get().user, self.user)

    def test_order_without_products_is_rejected(self):
        self.auth()
        response = self.client.post(self.url, {"products_id": []}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_only_sees_own_orders(self):
        mine = Order.objects.create(user=self.user)
        mine.products.add(self.p1)
        theirs = Order.objects.create(user=self.other)
        theirs.products.add(self.p2)
        self.auth()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], mine.id)


class TokenAuthTestCase(APITestCase):
    def test_obtain_token(self):
        User.objects.create_user("tester", password="pass12345")
        response = self.client.post(
            "/api-token-auth/", {"username": "tester", "password": "pass12345"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_wrong_password_is_rejected(self):
        User.objects.create_user("tester", password="pass12345")
        response = self.client.post(
            "/api-token-auth/", {"username": "tester", "password": "errada"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
