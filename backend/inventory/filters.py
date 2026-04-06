import django_filters
from django.db import models as db_models
from .models import StoreProduct

class StoreProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="selling_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="selling_price", lookup_expr="lte")
    category = django_filters.UUIDFilter(field_name="category__id")
    category_name = django_filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_favorite = django_filters.BooleanFilter(field_name="is_favorite")
    low_stock = django_filters.BooleanFilter(method="filter_low_stock")
    barcode = django_filters.CharFilter(field_name="barcode", lookup_expr="exact")
    
    class Meta:
        model = StoreProduct
        fields = [
            "is_active",
            "is_favorite",
            "category",
            "category_name",
            "min_price",
            "max_price",
            "low_stock",
            "barcode",
        ]

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__lte=db_models.F("low_stock_threshold"))
        return queryset.filter(stock_quantity__gt=db_models.F("low_stock_threshold"))
