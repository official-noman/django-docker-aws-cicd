import logging
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from stores.permissions import HasStoreAccess, SubscriptionIsActive
from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer

logger = logging.getLogger("orders")


@extend_schema_view(
    list=extend_schema(tags=["POS & Orders"]),
    create=extend_schema(tags=["POS & Orders"], request=OrderCreateSerializer, responses={201: OrderReadSerializer}),
    retrieve=extend_schema(tags=["POS & Orders"]),
)
class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Handle checking out a cart and creating an order in the POS system.
    Calculates totals, deducts inventory, and records customer dues automatically.
    """
    permission_classes = [IsAuthenticated, HasStoreAccess, SubscriptionIsActive]
    ordering_fields = ["created_at", "total_amount"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        return Order.objects.filter(store=self.request.store).prefetch_related("items")

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderReadSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        order = write_serializer.save()
        
        logger.info(
            "Order %s created: store=%s total=%s method=%s",
            order.id, request.store.name, order.total_amount, order.payment_method
        )
        
        # Read format for response
        read_serializer = OrderReadSerializer(order)
        return Response({
            "success": True,
            "message": "Order completed successfully.",
            "data": read_serializer.data
        }, status=status.HTTP_201_CREATED)
