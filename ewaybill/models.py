from django.db import models

class EWayBill(models.Model):

    EWAYBILL_STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('Generated', 'Generated'),
        ('Closed',    'Closed'),
        ('Cancelled', 'Cancelled'),
    ]

    challan_number   = models.CharField(max_length=100, unique=True)
    invoice_number   = models.CharField(max_length=100, blank=True, null=True)

    customer_name    = models.CharField(max_length=255)
    customer_gstin   = models.CharField(max_length=15, blank=True, null=True)

    challan_date     = models.DateField()
    vehicle_number   = models.CharField(max_length=20)
    transporter_id   = models.CharField(max_length=100, blank=True, null=True)
    transporter_name = models.CharField(max_length=255, blank=True, null=True)

    from_place       = models.CharField(max_length=255, blank=True, null=True)
    to_place         = models.CharField(max_length=255, blank=True, null=True)
    distance_km      = models.PositiveIntegerField(default=0)

    total_value      = models.DecimalField(max_digits=14, decimal_places=2)

    ewaybill_number  = models.CharField(max_length=100, blank=True, null=True, unique=True)
    ewaybill_status  = models.CharField(max_length=20, choices=EWAYBILL_STATUS_CHOICES, default='Pending')
    valid_upto       = models.DateTimeField(blank=True, null=True)
    generated_at     = models.DateTimeField(blank=True, null=True)

    cancellation_reason = models.TextField(blank=True, null=True)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-challan_date', '-created_at']

    def __str__(self):
        return f"{self.challan_number} – {self.customer_name} [{self.ewaybill_status}]"

class EWayBillAuditLog(models.Model):
    e_way_bill  = models.ForeignKey(EWayBill, on_delete=models.CASCADE, related_name='audit_logs')
    action      = models.CharField(max_length=50)          # Generated | Closed | Cancelled | Updated
    remarks     = models.TextField(blank=True, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.e_way_bill.challan_number} – {self.action} @ {self.performed_at}"