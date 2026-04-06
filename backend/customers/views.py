import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from stores.permissions import HasStoreAccess, SubscriptionIsActive
from .models import Customer
from .serializers import CustomerSerializer, DuePaymentSerializer

logger = logging.getLogger("customers")

@extend_schema_view(
    list=extend_schema(tags=["Customers (Bakir Khata)"]),
    create=extend_schema(tags=["Customers (Bakir Khata)"]),
    retrieve=extend_schema(tags=["Customers (Bakir Khata)"]),
    update=extend_schema(tags=["Customers (Bakir Khata)"]),
    partial_update=extend_schema(tags=["Customers (Bakir Khata)"]),
    destroy=extend_schema(tags=["Customers (Bakir Khata)"]),
)
class CustomerViewSet(viewsets.ModelViewSet):
    """
    CRUD for store's customers. Records dues and payments.
    Both Owners and Staff can manage customers.
    """
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess, SubscriptionIsActive]
    search_fields = ["name", "phone"]
    ordering_fields = ["name", "total_due", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Customer.objects.filter(store=self.request.store)

    def perform_create(self, serializer):
        serializer.save(store=self.request.store)

    @extend_schema(
        request=DuePaymentSerializer,
        responses={200: CustomerSerializer},
        tags=["Customers (Bakir Khata)"]
    )
    @action(detail=True, methods=["post"], url_path="pay-due")
    def pay_due(self, request, pk=None):
        """
        Record a payment towards a customer's outstanding due balance.
        """
        customer = self.get_object()
        serializer = DuePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount_paid = serializer.validated_data["amount_paid"]
        
        if amount_paid > customer.total_due:
            return Response(
                {"success": False, "error": {"message": "Payment amount exceeds total due."}},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        customer.total_due -= amount_paid
        customer.save()
        
        logger.info(
            "Due payment received: store=%s, customer=%s, amount=%s", 
            request.store.name, customer.name, amount_paid
        )
        
        return Response({
            "success": True,
            "message": f"Successfully paid {amount_paid}. Remaining due: {customer.total_due}",
            "data": CustomerSerializer(customer).data
        })
