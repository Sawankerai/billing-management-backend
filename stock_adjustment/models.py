from django.db import models
from core.models import Product


class StockAdjustment(models.Model):

    ADJUSTMENT_TYPE_CHOICES = [
        ('Add', 'Add'),
        ('Remove', 'Remove'),
        ('Damaged', 'Damaged'),
        ('Manual Correction', 'Manual Correction'),
        ('Expired', 'Expired'),
        ('Return', 'Return'),
        ('Transfer', 'Transfer'),
    ]

    DIRECTION_CHOICES = [
        ('Add', 'Add'),
        ('Reduce', 'Reduce'),
    ]

    REASON_CHOICES = [
        ('Manual Count', 'Manual Count'),
        ('Damaged Goods', 'Damaged Goods'),
        ('Expired Stock', 'Expired Stock'),
        ('Supplier Return', 'Supplier Return'),
        ('Customer Return', 'Customer Return'),
        ('Internal Use', 'Internal Use'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Pending Review', 'Pending Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    WAREHOUSE_CHOICES = [
        ('Main Store', 'Main Store'),
        ('Warehouse A', 'Warehouse A'),
        ('Warehouse B', 'Warehouse B'),
    ]

    adjustment_id     = models.AutoField(primary_key=True)
    adjustment_number = models.CharField(max_length=100, unique=True, editable=False, null=True)
    product           = models.ForeignKey(Product, on_delete=models.PROTECT)
    adjustment_type   = models.CharField(max_length=50, choices=ADJUSTMENT_TYPE_CHOICES)
    direction         = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='Add')
    reason            = models.CharField(max_length=50, choices=REASON_CHOICES)
    reference         = models.CharField(max_length=100, blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    warehouse         = models.CharField(max_length=100, choices=WAREHOUSE_CHOICES, default='Main Store')
    bin_location      = models.CharField(max_length=100, blank=True)

    quantity_before   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adjusted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_after    = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    adjustment_date   = models.DateField()
    notes             = models.TextField(blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.adjustment_number:
            import random, datetime
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.adjustment_number = f'ADJ-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adjustment_number} - {self.product}"


class StockAdjustmentItem(models.Model):
    adjustment        = models.ForeignKey(StockAdjustment, related_name='items', on_delete=models.CASCADE)
    product           = models.ForeignKey(Product, on_delete=models.PROTECT)
    description       = models.TextField(blank=True)
    quantity_before   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adjusted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_after    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit              = models.CharField(max_length=50, blank=True)
    bin_location      = models.CharField(max_length=100, blank=True)
    notes             = models.TextField(blank=True)

    def __str__(self):
        return f"{self.adjustment.adjustment_number} - {self.product}"