from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem, PaymentMethod
from inventory.models import StoreProduct
from customers.models import Customer


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "product_id", "product_name", "quantity", "unit_price", "subtotal")


class OrderCreateSerializer(serializers.Serializer):
    """
    Handles complete order creation in a single transaction:
    - Calculates totals
    - Deducts product stock
    - Updates customer due if applicable
    """
    items = OrderItemCreateSerializer(many=True, allow_empty=False)
    customer_id = serializers.UUIDField(required=False, allow_null=True)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices, default=PaymentMethod.CASH)

    def validate(self, attrs):
        store = self.context["request"].store
        payment_method = attrs.get("payment_method")
        customer_id = attrs.get("customer_id")
        
        if payment_method == PaymentMethod.DUE and not customer_id:
            raise serializers.ValidationError({"customer_id": "Customer is required for DUE payment types."})
            
        if customer_id:
            # Verify customer belongs to store
            if not Customer.objects.filter(id=customer_id, store=store).exists():
                raise serializers.ValidationError({"customer_id": "Invalid customer for this store."})
                
        # Validate items
        products_info = []
        for item in attrs["items"]:
            prod = StoreProduct.objects.filter(id=item["product_id"], store=store).first()
            if not prod:
                raise serializers.ValidationError({"items": f"Product UUID {item['product_id']} not found in your store."})
            if not prod.is_active:
                raise serializers.ValidationError({"items": f"Product {prod.name} is inactive."})
            if prod.stock_quantity < item["quantity"]:
                raise serializers.ValidationError({"items": f"Insufficient stock for {prod.name}. Available: {prod.stock_quantity}."})
                
            products_info.append({
                "product": prod,
                "quantity": item["quantity"]
            })
            
        attrs["_validated_products"] = products_info
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        store = self.context["request"].store
        store_user = self.context["request"].store_user
        
        discount = validated_data.get("discount", 0)
        paid_amount = validated_data.get("paid_amount", 0)
        payment_method = validated_data.get("payment_method")
        customer_id = validated_data.get("customer_id")
        
        subtotal = 0
        order_items_data = []
        
        # 1. Process items, calculate subtotal, deduct stock
        for p_info in validated_data["_validated_products"]:
            prod = p_info["product"]
            qty = p_info["quantity"]
            
            unit_price = prod.selling_price
            item_sub = unit_price * qty
            subtotal += item_sub
            
            order_items_data.append(dict(
                product=prod,
                product_name=prod.name,
                quantity=qty,
                unit_price=unit_price,
                subtotal=item_sub
            ))
            
            # Deduct stock
            prod.stock_quantity -= qty
            prod.save(update_fields=["stock_quantity"])
            
        total_amount = subtotal - discount
        due_amount = total_amount - paid_amount if (total_amount > paid_amount) else 0

        # Create Order
        order = Order.objects.create(
            store=store,
            handled_by=store_user,
            customer_id=customer_id,
            subtotal=subtotal,
            discount=discount,
            total_amount=total_amount,
            paid_amount=paid_amount,
            due_amount=due_amount,
            payment_method=payment_method
        )
        
        # Bulk create items
        item_objects = [OrderItem(order=order, **i_data) for i_data in order_items_data]
        OrderItem.objects.bulk_create(item_objects)
        
        # 3. Handle Bakir Khata (Customer Due)
        if due_amount > 0 and customer_id:
            customer = Customer.objects.get(id=customer_id)
            customer.total_due += due_amount
            customer.save(update_fields=["total_due"])
            
        return order


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True, default=None)
    handled_by_name = serializers.CharField(source="handled_by.user.username", read_only=True, default=None)

    class Meta:
        model = Order
        fields = (
            "id", "customer", "customer_name", "handled_by_name",
            "subtotal", "discount", "total_amount", "paid_amount", "due_amount",
            "payment_method", "created_at", "items"
        )
