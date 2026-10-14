from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from order.models import Order
from order.serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("products").order_by("id")
        user = self.request.user
        # cada usuário só enxerga os próprios pedidos (staff vê todos)
        return queryset if user.is_staff else queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
