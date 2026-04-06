from django.contrib import admin
from .models import Category, GlobalProduct, StoreProduct


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "slug", "created_at")
    list_filter = ("store",)
    search_fields = ("name", "store__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("store",)


@admin.register(GlobalProduct)
class GlobalProductAdmin(admin.ModelAdmin):
    list_display = ("name", "barcode", "default_mrp", "created_at")
    search_fields = ("name", "barcode")
    readonly_fields = ("id", "created_at")


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "store",
        "barcode",
        "category",
        "cost_price",
        "selling_price",
        "stock_quantity",
        "is_active",
        "is_favorite",
    )
    list_filter = ("store", "is_active", "is_favorite", "category", "created_at")
    search_fields = ("name", "sku", "barcode", "description", "store__name")
    readonly_fields = ("id", "created_at", "updated_at")
    list_editable = ("cost_price", "selling_price", "stock_quantity", "is_active", "is_favorite")
    list_per_page = 25
    raw_id_fields = ("store", "category", "global_product")
