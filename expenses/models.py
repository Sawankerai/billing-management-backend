from django.db import models

class Expense(models.Model):

    CATEGORY_CHOICES = [
        ('travel_transport', 'Travel & Transport'),
        ('office_supplies',  'Office Supplies'),
        ('marketing_ads',    'Marketing & Ads'),
        ('it_software',      'IT & Software'),
        ('rent',             'Rent'),
        ('legal',            'Legal'),
    ]

    PAID_VIA_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('card',          'Card'),
        ('upi',           'UPI'),
        ('cash',          'Cash'),
    ]

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending',  'Pending'),
        ('rejected', 'Rejected'),
    ]

    expense_no   = models.CharField(max_length=50, unique=True, editable=False)
    category     = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date         = models.DateField()
    vendor_payee = models.CharField(max_length=200)
    amount       = models.DecimalField(max_digits=12, decimal_places=2)   # base amount (excl. GST)
    cgst_rate    = models.DecimalField(max_digits=5, decimal_places=2, default=9.00)
    sgst_rate    = models.DecimalField(max_digits=5, decimal_places=2, default=9.00)
    paid_via     = models.CharField(max_length=30, choices=PAID_VIA_CHOICES)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes        = models.TextField(blank=True)
    reference    = models.CharField(max_length=100, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    # Auto-generate expense number like EXP-260226-101
    def save(self, *args, **kwargs):
        if not self.expense_no:
            from django.utils import timezone
            date_str = timezone.now().strftime('%y%m%d')
            last = Expense.objects.filter(
                expense_no__startswith=f'EXP-{date_str}-'
            ).order_by('expense_no').last()
            seq = int(last.expense_no.split('-')[-1]) + 1 if last else 101
            self.expense_no = f'EXP-{date_str}-{seq}'
        super().save(*args, **kwargs)

    # Computed GST fields (read-only, not stored)
    @property
    def cgst_amount(self):
        return round(self.amount * self.cgst_rate / 100, 2)

    @property
    def sgst_amount(self):
        return round(self.amount * self.sgst_rate / 100, 2)

    @property
    def total_amount(self):
        return self.amount + self.cgst_amount + self.sgst_amount

    def __str__(self):
        return f"{self.expense_no} - {self.vendor_payee}"