from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from product.models import Category, Product
from product.serializers import CategorySerializer, ProductSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.prefetch_related("categories").order_by("id")


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all().order_by("id")
