from django.db import models

class ExpenseCategory(models.Model):

    STATUS_CHOICES = [
        ('active',   'Active'),
        ('inactive', 'Inactive'),
        ('blocked',  'Blocked'),
    ]

    name        = models.CharField(max_length=100, unique=True)   # Travel & Transport
    code        = models.CharField(max_length=50,  unique=True)   # CAT-TRAVEL
    default_tax = models.DecimalField(max_digits=5, decimal_places=2)  # 5.00 / 18.00
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes       = models.TextField(blank=True)                    # Default category
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name        = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        ordering            = ['name']