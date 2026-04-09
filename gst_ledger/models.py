from django.db import models


class GSTLedger(models.Model):

    LEDGER_TYPE_CHOICES = [
        ('Input', 'Input'),
        ('Output', 'Output'),
    ]

    VOUCHER_TYPE_CHOICES = [
        ('Expense', 'Expense'),
        ('Sales Invoice', 'Sales Invoice'),
        ('Purchase Invoice', 'Purchase Invoice'),
        ('Credit Note', 'Credit Note'),
        ('Debit Note', 'Debit Note'),
        ('Journal', 'Journal'),
    ]

    ledger_type  = models.CharField(max_length=10, choices=LEDGER_TYPE_CHOICES)
    voucher_type = models.CharField(max_length=50, choices=VOUCHER_TYPE_CHOICES)
    ref          = models.CharField(max_length=100, unique=True)
    date         = models.DateField()
    debit        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cess         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gstin        = models.CharField(max_length=15, blank=True, null=True)
    party_name   = models.CharField(max_length=255, blank=True, null=True)
    narration    = models.TextField(blank=True, null=True)
    is_posted    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gst_ledger'
        ordering = ['-date', '-created_at']
        verbose_name = 'GST Ledger Entry'
        verbose_name_plural = 'GST Ledger Entries'

    def __str__(self):
        return f"{self.ledger_type} | {self.voucher_type} | {self.ref} | {self.date}"