from rest_framework import serializers

from order.models import Order
from product.models import Product
from product.serializers import ProductSerializer


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductSerializer(source="products", many=True, read_only=True)
    products_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        many=True,
        allow_empty=False,
        source="products",
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "product", "products_id", "total", "created_at"]

    def get_total(self, instance):
        return sum(product.price or 0 for product in instance.products.all())
