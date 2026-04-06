import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Store / Tenant
# ---------------------------------------------------------------------------
class Store(models.Model):
    """
    Each Store is an isolated tenant.
    All business data (products, categories, users) belong to exactly one Store.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    address = models.TextField(blank=True, default="")
    logo = models.URLField(blank=True, default="", help_text="CDN URL for store logo")
    currency = models.CharField(max_length=3, default="USD")
    timezone = models.CharField(max_length=50, default="UTC")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------
class SubscriptionPlan(models.TextChoices):
    TRIAL = "trial", "Trial"
    BASIC = "basic", "Basic"
    PRO = "pro", "Professional"
    ENTERPRISE = "enterprise", "Enterprise"


class Subscription(models.Model):
    """
    Tracks billing plan and trial status per Store.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.OneToOneField(
        Store, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.TRIAL,
    )
    trial_start_date = models.DateTimeField(default=timezone.now)
    trial_end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    max_products = models.IntegerField(
        default=50, help_text="Product limit for this plan"
    )
    max_staff = models.IntegerField(
        default=2, help_text="Staff member limit for this plan"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.store.name} — {self.get_plan_display()}"

    def save(self, *args, **kwargs):
        if not self.trial_end_date and self.plan == SubscriptionPlan.TRIAL:
            self.trial_end_date = self.trial_start_date + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_trial_expired(self):
        if self.plan != SubscriptionPlan.TRIAL:
            return False
        return timezone.now() > self.trial_end_date if self.trial_end_date else False

    @property
    def days_remaining(self):
        if self.plan != SubscriptionPlan.TRIAL or not self.trial_end_date:
            return None
        delta = (self.trial_end_date - timezone.now()).days
        return max(delta, 0)


# ---------------------------------------------------------------------------
# Store User (Role-based membership)
# ---------------------------------------------------------------------------
class StoreRole(models.TextChoices):
    OWNER = "owner", "Store Owner"
    STAFF = "staff", "Staff"


class StoreUser(models.Model):
    """
    Links a Django User to a Store with a specific role.
    A user can belong to multiple stores (e.g. a consultant managing several shops).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_memberships",
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="members"
    )
    role = models.CharField(
        max_length=10,
        choices=StoreRole.choices,
        default=StoreRole.STAFF,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "store")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} @ {self.store.name} [{self.get_role_display()}]"

    @property
    def is_owner(self):
        return self.role == StoreRole.OWNER
