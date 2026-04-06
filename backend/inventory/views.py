import logging
from django.utils import timezone
from django.db.models import Sum, Count, F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from stores.permissions import HasStoreAccess, IsOwnerOrStockUpdate, IsStoreOwnerOrReadOnly, SubscriptionIsActive
from .models import Category, GlobalProduct, StoreProduct
from .serializers import CategorySerializer, GlobalProductSerializer, StoreProductSerializer, StoreProductCreateUpdateSerializer
from .filters import StoreProductFilter
from orders.models import Order, OrderItem
from customers.models import Customer

logger = logging.getLogger("inventory")


@extend_schema_view(
    list=extend_schema(tags=["Categories"]),
    create=extend_schema(tags=["Categories"]),
    retrieve=extend_schema(tags=["Categories"]),
    update=extend_schema(tags=["Categories"]),
    destroy=extend_schema(tags=["Categories"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, HasStoreAccess, IsStoreOwnerOrReadOnly, SubscriptionIsActive]
    
    def get_queryset(self):
        return Category.objects.filter(store=self.request.store)

    def perform_create(self, serializer):
        serializer.save(store=self.request.store)


@extend_schema_view(
    list=extend_schema(tags=["Global Models"]),
    retrieve=extend_schema(tags=["Global Models"])
)
class GlobalProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only catalog for looking up barcodes globally.
    """
    queryset = GlobalProduct.objects.all()
    serializer_class = GlobalProductSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(tags=["Global Models"])
    @action(detail=False, methods=["get"], url_path="scan/(?P<barcode>[^/.]+)")
    def scan(self, request, barcode=None):
        prod = GlobalProduct.objects.filter(barcode=barcode).first()
        if not prod:
            return Response({"success": False, "message": "Barcode not found in global catalog."}, status=404)
        return Response({"success": True, "data": GlobalProductSerializer(prod).data})


@extend_schema_view(
    list=extend_schema(tags=["Store Products"]),
    create=extend_schema(tags=["Store Products"]),
    retrieve=extend_schema(tags=["Store Products"]),
    update=extend_schema(tags=["Store Products"]),
    partial_update=extend_schema(tags=["Store Products"]),
    destroy=extend_schema(tags=["Store Products"]),
)
class StoreProductViewSet(viewsets.ModelViewSet):
    """
    POS Inventory endpoints. Staff can adjust stock and view, Owners can edit structure.
    """
    permission_classes = [IsAuthenticated, HasStoreAccess, IsOwnerOrStockUpdate, SubscriptionIsActive]
    filterset_class = StoreProductFilter
    search_fields = ["name", "sku", "barcode"]
    ordering_fields = ["name", "stock_quantity"]
    
    def get_queryset(self):
        qs = StoreProduct.objects.filter(store=self.request.store).select_related("category")
        if self.request.query_params.get("favorites") == "true":
            qs = qs.filter(is_favorite=True)
        return qs

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return StoreProductCreateUpdateSerializer
        return StoreProductSerializer

    def perform_create(self, serializer):
        serializer.save(store=self.request.store)

    @extend_schema(tags=["Store Products"])
    @action(detail=False, methods=["get"], url_path="scan/(?P<barcode>[^/.]+)")
    def scan(self, request, barcode=None):
        """Lookup in local store."""
        prod = self.get_queryset().filter(barcode=barcode).first()
        if not prod:
            # Fallback advice
            return Response({
                "success": False, 
                "error": "Not registered in your store. Try global scan to auto-fill."
            }, status=404)
        return Response({"success": True, "data": StoreProductSerializer(prod).data})


class DashboardStatisticsView(APIView):
    """
    BI Dashboard APIs for Store Owners.
    """
    permission_classes = [IsAuthenticated, HasStoreAccess]

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        store = request.store
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today_start.replace(day=1)

        # 1. Today's sales
        todays_orders = Order.objects.filter(store=store, created_at__gte=today_start)
        today_revenue = todays_orders.aggregate(total=Sum("total_amount"))["total"] or 0

        # 2. Total outstanding due
        customers = Customer.objects.filter(store=store)
        total_due = customers.aggregate(total=Sum("total_due"))["total"] or 0

        # 3. Low stock products
        low_stock_products = StoreProduct.objects.filter(
            store=store, 
            is_active=True,
            stock_quantity__lte=F("low_stock_threshold")
        ).order_by("stock_quantity")[:10]

        # 4. Top 5 Best-Selling Products This Month
        # Join OrderItem -> Order -> Store
        best_sellers_qs = OrderItem.objects.filter(
            order__store=store, 
            order__created_at__gte=month_start
        ).values('product__id', 'product_name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]

        return Response({
            "success": True,
            "data": {
                "today_sales_revenue": float(today_revenue),
                "total_outstanding_due": float(total_due),
                "low_stock_products": StoreProductSerializer(low_stock_products, many=True).data,
                "top_selling_products": list(best_sellers_qs)
            }
        })