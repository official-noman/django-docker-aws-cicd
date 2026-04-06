from rest_framework import serializers
from .models import Category, GlobalProduct, StoreProduct

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "created_at")


class GlobalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalProduct
        fields = ("id", "barcode", "name", "description", "default_mrp")


class StoreProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = StoreProduct
        fields = (
            "id", "name", "sku", "barcode", "description",
            "cost_price", "selling_price", "stock_quantity", "low_stock_threshold",
            "category", "category_name", "is_favorite", "is_active", "is_low_stock",
            "global_product"
        )
        read_only_fields = ("id",)


class StoreProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProduct
        fields = (
            "name", "sku", "barcode", "description",
            "cost_price", "selling_price", "stock_quantity", "low_stock_threshold",
            "category", "is_favorite", "is_active", "global_product"
        )

    def validate_selling_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Selling price cannot be negative.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value