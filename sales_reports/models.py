from django.db import models


class SalesReport(models.Model):
   

    STATUS_CHOICES = [
        ('paid',         'Paid'),
        ('partial',      'Partial'),
        ('outstanding',  'Outstanding'),
        ('overdue',      'Overdue'),
    ]

    invoice_no     = models.CharField(max_length=50, unique=True)   
    date           = models.DateField()                              
    customer_name  = models.CharField(max_length=200)              
    company        = models.CharField(max_length=200, blank=True)   
    item           = models.CharField(max_length=200)               
    category       = models.CharField(max_length=100, blank=True)
    qty_sold       = models.PositiveIntegerField(default=1)
    taxable        = models.DecimalField(max_digits=12, decimal_places=2)  
    tax            = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_sales    = models.DecimalField(max_digits=12, decimal_places=2) 
    returns        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid           = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date       = models.DateField(null=True, blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='outstanding')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    # Computed properties
    @property
    def net_sales(self):
        return self.gross_sales - self.returns

    @property
    def outstanding(self):
        return self.gross_sales - self.paid

    def __str__(self):
        return f"{self.invoice_no} - {self.customer_name}"

    class Meta:
        ordering = ['-date']