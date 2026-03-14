from django.db import models
from core.models import Product


class Batch(models.Model):

    BATCH_STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Released', 'Released'),
        ('Quarantine', 'Quarantine'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    ]

    QA_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Passed', 'Passed'),
        ('Failed', 'Failed'),
    ]

    batch_id     = models.AutoField(primary_key=True)
    product      = models.ForeignKey(Product, on_delete=models.PROTECT)
    sku          = models.CharField(max_length=100, blank=True)
    batch_number = models.CharField(max_length=100, unique=True, editable=False)

    received_on  = models.DateField()
    expiry_date  = models.DateField(null=True, blank=True)

    total_units      = models.PositiveIntegerField(default=0)
    available_units  = models.PositiveIntegerField(default=0)
    reserved_units   = models.PositiveIntegerField(default=0)
    damaged_units    = models.PositiveIntegerField(default=0)

    bin_location = models.CharField(max_length=100, blank=True)

    batch_status = models.CharField(
        max_length=20,
        choices=BATCH_STATUS_CHOICES,
        default='Pending'
    )

    qa_status = models.CharField(
        max_length=20,
        choices=QA_STATUS_CHOICES,
        default='Pending'
    )

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.batch_number:
            import random, datetime
            today = datetime.date.today().strftime('%y%m%d')
            rand  = random.randint(100, 999)
            self.batch_number = f'BATCH-{today}-{rand}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Batch {self.batch_number} - {self.product}"


# Batch Items
class BatchItem(models.Model):

    batch   = models.ForeignKey(
        Batch,
        related_name='items',
        on_delete=models.CASCADE
    )
    product     = models.ForeignKey(Product, on_delete=models.PROTECT)
    sku         = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    quantity        = models.DecimalField(max_digits=10, decimal_places=2)
    unit            = models.CharField(max_length=50)
    cost_per_unit   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost      = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    expiry_date  = models.DateField(null=True, blank=True)
    bin_location = models.CharField(max_length=100, blank=True)
    notes        = models.TextField(blank=True)

    def __str__(self):
        return f"{self.batch.batch_number} - {self.product}"

