import uuid
from django.db import models


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    DUE = "DUE", "Due (Bakir Khata)"
    DIGITAL = "DIGITAL", "Digital Payment (MFS/Card)"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="orders")
    
    # Track who made the sale
    handled_by = models.ForeignKey("stores.StoreUser", on_delete=models.SET_NULL, null=True, related_name="handled_orders")
    
    # Required if payment is DUE, optional otherwise
    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # subtotal - discount
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} - Store: {self.store.name} - Total: {self.total_amount}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("inventory.StoreProduct", on_delete=models.SET_NULL, null=True, related_name="order_history")
    
    # Snapshot of data since product price/name might change
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2) # quantity * unit_price

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (Order {self.order.id})"
