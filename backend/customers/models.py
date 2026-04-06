import uuid
from django.db import models


class Customer(models.Model):
    """
    Store-specific customer for 'Bakir Khata' (due management).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="customers"
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, default="")
    address = models.TextField(blank=True, default="")
    total_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Total outstanding amount."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("store", "phone")  # Phone must be unique within a store

    def __str__(self):
        return f"{self.name} ({self.phone}) - Due: {self.total_due}"
