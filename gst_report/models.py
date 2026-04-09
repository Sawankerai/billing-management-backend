from django.db import models


class GSTTransaction(models.Model):

    TRANSACTION_TYPE_CHOICES = [
        ('Output', 'Output'),
        ('Input',  'Input'),
    ]

    INVOICE_STATUS_CHOICES = [
        ('Paid',      'Paid'),
        ('Unpaid',    'Unpaid'),
        ('Cancelled', 'Cancelled'),
        ('Returns',   'Returns'),
    ]

    TAX_RATE_CHOICES = [
        (0,  '0%'),
        (5,  '5%'),
        (12, '12%'),
        (18, '18%'),
        (28, '28%'),
    ]

    transaction_type   = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date   = models.DateField()
    invoice_number     = models.CharField(max_length=100)
    gstin              = models.CharField(max_length=15, blank=True, null=True)
    state_code         = models.CharField(max_length=5, blank=True, null=True)
    party_name         = models.CharField(max_length=255, blank=True, null=True)
    invoice_status     = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='Paid')
    taxable_amount     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cgst_amount        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sgst_amount        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    igst_amount        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_rate           = models.IntegerField(choices=TAX_RATE_CHOICES, default=18)
    is_reverse_charge  = models.BooleanField(default=False)
    is_nil_exempt      = models.BooleanField(default=False)
    is_non_gst         = models.BooleanField(default=False)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date', '-created_at']

    def total_tax(self):
        return self.cgst_amount + self.sgst_amount + self.igst_amount

    def __str__(self):
        return f"{self.transaction_type} | {self.invoice_number} | {self.transaction_date}"