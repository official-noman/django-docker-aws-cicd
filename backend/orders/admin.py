from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("id", "subtotal")
    raw_id_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "store", "handled_by", "customer", "total_amount", "due_amount", "payment_method", "created_at")
    list_filter = ("store", "payment_method", "created_at")
    search_fields = ("id", "store__name", "customer__name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("store", "handled_by", "customer")
    inlines = [OrderItemInline]
