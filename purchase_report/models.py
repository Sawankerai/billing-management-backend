from decimal import Decimal

from django.db import models
from django.db.models import Sum


class PurchaseOrder(models.Model):
    PO_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("partially_received", "Partially Received"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    ]

    DEBIT_NOTE_STATUS_CHOICES = [
        ("none", "None"),
        ("draft", "Draft"),
        ("non_draft", "Non-Draft"),
    ]

    bill_number = models.CharField(max_length=50, unique=True, blank=True)
    order_date = models.DateField()
    expected_receipt_date = models.DateField(null=True, blank=True)
    vendor_name = models.CharField(max_length=150)
    vendor_company = models.CharField(max_length=180, blank=True)
    po_status = models.CharField(
        max_length=30,
        choices=PO_STATUS_CHOICES,
        default="open",
    )
    debit_note_status = models.CharField(
        max_length=20,
        choices=DEBIT_NOTE_STATUS_CHOICES,
        default="non_draft",
    )
    received_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-order_date", "-id"]

    def __str__(self):
        return self.bill_number or f"PO-{self.pk}"

    def _item_sum(self, field_name):
        prefetched = getattr(self, "_prefetched_objects_cache", {})
        if "items" in prefetched:
            return sum(
                (getattr(item, field_name) or Decimal("0.00"))
                for item in prefetched["items"]
            )

        value = self.items.aggregate(total=Sum(field_name))["total"]
        return value or Decimal("0.00")

    @property
    def taxable_value(self):
        return self._item_sum("taxable_value")

    @property
    def input_tax(self):
        return self._item_sum("tax_amount")

    @property
    def gross_purchases(self):
        return self._item_sum("gross_purchases")

    @property
    def returns_adjustments(self):
        return self._item_sum("returns_adjustments")

    @property
    def net_purchases(self):
        return self._item_sum("net_purchases")

    @property
    def pending_value(self):
        pending = self.net_purchases - self.received_value
        return pending if pending > 0 else Decimal("0.00")


class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(
        PurchaseOrder,
        related_name="items",
        on_delete=models.CASCADE,
    )
    item_name = models.CharField(max_length=180)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    qty_ordered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    qty_returned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    taxable_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    gross_purchases = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    returns_adjustments = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    net_purchases = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.item_name

    def save(self, *args, **kwargs):
        if not self.gross_purchases:
            self.gross_purchases = self.taxable_value + self.tax_amount
        if not self.net_purchases:
            net = self.gross_purchases - self.returns_adjustments
            self.net_purchases = net if net > 0 else Decimal("0.00")
        super().save(*args, **kwargs)