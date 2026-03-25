from django.db import models


class Account(models.Model):

    ACCOUNT_TYPE_CHOICES = [
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Equity', 'Equity'),
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    BALANCE_TYPE_CHOICES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    account_code = models.CharField(max_length=50, blank=True, null=True)
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_type = models.CharField(max_length=10, choices=BALANCE_TYPE_CHOICES, default='Debit')
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_code} — {self.account_name}"

    class Meta:
        db_table = 'accounts'
        ordering = ['account_code', 'account_name']