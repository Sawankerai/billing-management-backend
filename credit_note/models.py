from django.db import models
from core.models import Customer


class CreditNote(models.Model):

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Issued', 'Issued'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    ]

    REASON_CHOICES = [
        ('Returned items', 'Returned items'),
        ('Pricing adjustment', 'Pricing adjustment'),
        ('Damaged shipment', 'Damaged shipment'),
        ('Duplicate invoice', 'Duplicate invoice'),
        ('Other', 'Other'),
    ]

    credit_note_number = models.CharField(max_length=50, unique=True, editable=False, null=True)
    customer           = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date               = models.DateField()
    reference          = models.CharField(max_length=100, blank=True)  # Invoice number e.g. INV-240201
    reason             = models.CharField(max_length=50, choices=REASON_CHOICES)
    value              = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes              = models.TextField(blank=True)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.credit_note_number:
            import datetime, random
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.credit_note_number = f'CN-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.credit_note_number