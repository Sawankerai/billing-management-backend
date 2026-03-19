from django.db import models
from django.utils import timezone


class BarcodeDevice(models.Model):
    DEVICE_STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
    ]

    name = models.CharField(max_length=100)  # e.g. Zebra DS2208
    device_uid = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=DEVICE_STATUS_CHOICES, default='disconnected')
    last_scan_barcode = models.CharField(max_length=200, blank=True, null=True)
    last_scan_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

    class Meta:
        db_table = 'barcode_devices'


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('stock_in', 'Stock In'),
        ('stock_out', 'Stock Out'),
        ('transfer', 'Transfer'),
    ]

    MOVEMENT_STATUS_CHOICES = [
        ('posted', 'Posted'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    movement_number = models.CharField(max_length=50, unique=True, editable=False)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    barcode = models.CharField(max_length=200, blank=True, null=True)
    sku = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    from_location = models.CharField(max_length=100, blank=True, null=True)
    to_location = models.CharField(max_length=100)
    reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=MOVEMENT_STATUS_CHOICES, default='posted')
    device = models.ForeignKey(
        BarcodeDevice, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='movements'
    )
    scanned_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.movement_number:
            prefix_map = {
                'stock_in': 'MOV',
                'stock_out': 'MOV',
                'transfer': 'TR',
            }
            prefix = prefix_map.get(self.movement_type, 'MOV')
            last = StockMovement.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.movement_number = f"{prefix}-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.movement_number} — {self.movement_type} — {self.product_name}"

    class Meta:
        db_table = 'stock_movements'
        ordering = ['-scanned_at']