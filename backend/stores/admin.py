from django.contrib import admin

from .models import Store, Subscription, StoreUser


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    readonly_fields = ("id", "created_at", "updated_at")


class StoreUserInline(admin.TabularInline):
    model = StoreUser
    extra = 0
    readonly_fields = ("id", "created_at")
    raw_id_fields = ("user",)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "email", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug", "email")
    readonly_fields = ("id", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubscriptionInline, StoreUserInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("store", "plan", "is_active", "trial_start_date", "trial_end_date")
    list_filter = ("plan", "is_active")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(StoreUser)
class StoreUserAdmin(admin.ModelAdmin):
    list_display = ("user", "store", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "store__name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("user",)
