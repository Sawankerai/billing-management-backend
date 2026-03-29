from django.db import models
from core.models import Customer


class Payment(models.Model):

    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
    ]

    GATEWAY_STATUS_CHOICES = [
        ('Initiated', 'Initiated'),
        ('Processing', 'Processing'),
        ('Cleared', 'Cleared'),
        ('Failed', 'Failed'),
        ('Reattempt', 'Reattempt'),
    ]

    ALLOCATION_STATUS_CHOICES = [
        ('Unallocated', 'Unallocated'),
        ('Partially Allocated', 'Partially Allocated'),
        ('Allocated', 'Allocated'),
        ('Overpayment', 'Overpayment'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Applied', 'Applied'),
        ('Unapplied', 'Unapplied'),
        ('Failed', 'Failed'),
        ('Processing', 'Processing'),
        ('Cancelled', 'Cancelled'),
    ]

    receipt_number      = models.CharField(max_length=50, unique=True, editable=False)
    customer            = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date                = models.DateField()
    payment_mode        = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES)
    amount              = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gateway_status      = models.CharField(max_length=20, choices=GATEWAY_STATUS_CHOICES, default='Initiated')
    allocation_status   = models.CharField(max_length=30, choices=ALLOCATION_STATUS_CHOICES, default='Unallocated')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unapplied')
    invoice_allocation  = models.TextField(blank=True)   # e.g. INV-240201 (₹9,200) - Advance ₹800
    advance_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes               = models.TextField(blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            import random, datetime
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.receipt_number = f'PAY-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.receipt_number