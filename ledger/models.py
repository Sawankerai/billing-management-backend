from django.db import models
from core.models import Customer, Vendor


class Invoice(models.Model):
    customer       = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='ledger_invoices'
    )
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    date           = models.DateField()
    amount         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import random, datetime
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.invoice_number = f'INV-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class Receipt(models.Model):
    customer       = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='ledger_receipts'
    )
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    date           = models.DateField()
    amount         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            import random, datetime
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.receipt_number = f'PAY-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.receipt_number


# ── Supplier Ledger Models ─────────────────────────────────────────────────────
class PurchaseInvoice(models.Model):
    vendor         = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name='ledger_purchase_invoices'
    )
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    date           = models.DateField()
    amount         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import random, datetime
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.invoice_number = f'PINV-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class SupplierPayment(models.Model):
    vendor         = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name='ledger_supplier_payments'
    )
    payment_number = models.CharField(max_length=50, unique=True, editable=False)
    date           = models.DateField()
    amount         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.payment_number:
            import random, datetime
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.payment_number = f'SPAY-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.payment_number