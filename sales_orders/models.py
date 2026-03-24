from django.db import models


class SalesOrder(models.Model):

    DISPATCH_STATUS_CHOICES = [
        ('open', 'Open'),
        ('partially_dispatched', 'Partially Dispatched'),
        ('dispatched', 'Dispatched'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    so_number = models.CharField(max_length=50, unique=True, editable=False)
    customer_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    order_date = models.DateField()
    expected_dispatch_date = models.DateField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    salesperson = models.CharField(max_length=255, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_items = models.PositiveIntegerField(default=0)
    dispatched_items = models.PositiveIntegerField(default=0)
    dispatch_status = models.CharField(max_length=30, choices=DISPATCH_STATUS_CHOICES, default='open')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.so_number:
            from django.utils import timezone
            today = timezone.now()
            prefix = f"SO-{today.strftime('%y%m%d')}"
            last = SalesOrder.objects.filter(
                so_number__startswith=prefix
            ).order_by('-id').first()
            if last:
                last_seq = int(last.so_number.split('-')[-1])
                seq = last_seq + 1
            else:
                seq = 1
            self.so_number = f"{prefix}-{seq:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.so_number} — {self.customer_name}"

    class Meta:
        db_table = 'sales_orders'
        ordering = ['-order_date']


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    dispatched_quantity = models.PositiveIntegerField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.rate and self.quantity:
            tax_amount = (self.rate * self.quantity) * (self.tax / 100)
            self.total_price = (self.rate * self.quantity) + tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sales_order.so_number} — {self.product_name}"

    class Meta:
        db_table = 'sales_order_items'