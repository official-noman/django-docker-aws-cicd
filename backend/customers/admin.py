from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "phone", "total_due", "created_at")
    list_filter = ("store",)
    search_fields = ("name", "phone", "store__name")
    readonly_fields = ("id", "total_due", "created_at", "updated_at")
    raw_id_fields = ("store",)
