from django.urls import include, path
from rest_framework import routers

from product import viewsets

router = routers.DefaultRouter()
router.register(r"product", viewsets.ProductViewSet, basename="product")
router.register(r"category", viewsets.CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
