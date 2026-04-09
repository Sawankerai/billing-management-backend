from django.db import models


class ITCReconciliation(models.Model):

    MATCH_STATUS_CHOICES = [
        ('Matched', 'Matched'),
        ('Pending', 'Pending'),
        ('Mismatch', 'Mismatch'),
        ('Resolved', 'Resolved'),
    ]

    MISMATCH_REASON_CHOICES = [
        ('Invoice Not Reflected', 'Invoice Not Reflected'),
        ('GSTIN Mismatch', 'GSTIN Mismatch'),
        ('Tax Amount Mismatch', 'Tax Amount Mismatch'),
        ('Invoice Date Mismatch', 'Invoice Date Mismatch'),
        ('Duplicate Entry', 'Duplicate Entry'),
        ('Cancelled Invoice', 'Cancelled Invoice'),
        ('Other', 'Other'),
    ]

    ELIGIBLE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Partial', 'Partial'),
    ]

    expense_ref      = models.CharField(max_length=100, unique=True)
    vendor_name      = models.CharField(max_length=255)
    vendor_gstin     = models.CharField(max_length=15)
    date             = models.DateField()
    tax_amount       = models.DecimalField(max_digits=12, decimal_places=2)
    cgst             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cess             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_value    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    match_status     = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='Pending')

    mismatch_reason  = models.CharField(max_length=50, choices=MISMATCH_REASON_CHOICES, blank=True, null=True)
    eligible         = models.CharField(max_length=10, choices=ELIGIBLE_CHOICES, blank=True, null=True)
    eligible_amount  = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    invoice_document = models.FileField(upload_to='itc_invoices/', blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at      = models.DateTimeField(blank=True, null=True)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'itc_reconciliation'
        ordering = ['-date', '-created_at']
        verbose_name = 'ITC Reconciliation'
        verbose_name_plural = 'ITC Reconciliations'

    def __str__(self):
        return f"{self.expense_ref} | {self.vendor_name} | {self.match_status}"