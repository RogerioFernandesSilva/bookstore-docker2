from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from product.models import Category, Product


class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tester", password="pass12345")
        self.token = Token.objects.create(user=self.user)
        self.category = Category.objects.create(title="Books", slug="books")
        self.product = Product.objects.create(title="Django", price=100)
        self.product.categories.add(self.category)
        self.url = "/bookstore/v1/product/"

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_with_token(self):
        self.auth()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["title"], "Django")
        self.assertEqual(result["category"][0]["slug"], "books")

    def test_create_product(self):
        self.auth()
        payload = {"title": "DRF", "price": 80, "categories_id": [self.category.id]}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        created = Product.objects.get(title="DRF")
        self.assertEqual(list(created.categories.all()), [self.category])

    def test_create_category(self):
        self.auth()
        payload = {"title": "Tech", "slug": "tech"}
        response = self.client.post("/bookstore/v1/category/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_v2_route_also_works(self):
        self.auth()
        response = self.client.get("/bookstore/v2/product/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
