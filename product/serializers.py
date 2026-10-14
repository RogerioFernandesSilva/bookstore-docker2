from rest_framework import serializers

from product.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug", "description", "active"]


class ProductSerializer(serializers.ModelSerializer):
    # leitura: categorias completas; escrita: lista de ids em "categories_id"
    category = CategorySerializer(source="categories", many=True, read_only=True)
    categories_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        many=True,
        required=False,
        source="categories",
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "active",
            "category",
            "categories_id",
        ]
