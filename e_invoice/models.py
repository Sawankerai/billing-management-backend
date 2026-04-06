from django.db import models
import uuid


class EInvoice(models.Model):

    IRN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Generated', 'Generated'),
        ('Cancelled', 'Cancelled'),
        ('Failed', 'Failed'),
    ]

    invoice_number   = models.CharField(max_length=50, unique=True)
    customer_name    = models.CharField(max_length=255)
    customer_gstin   = models.CharField(max_length=15, blank=True, null=True)
    invoice_date     = models.DateField()
    taxable_value    = models.DecimalField(max_digits=15, decimal_places=2)
    gst_amount       = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount     = models.DecimalField(max_digits=15, decimal_places=2)
    place_of_supply  = models.CharField(max_length=100, blank=True, null=True)
    hsn_sac_code     = models.CharField(max_length=20, blank=True, null=True)
    irn              = models.CharField(max_length=255, blank=True, null=True, unique=True)
    qr_code          = models.TextField(blank=True, null=True)
    irn_status       = models.CharField(max_length=20, choices=IRN_STATUS_CHOICES, default='Pending')
    irn_generated_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    is_eligible      = models.BooleanField(default=True)
    notes            = models.TextField(blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'e_invoice'
        ordering = ['-invoice_date']
        verbose_name = 'E-Invoice'
        verbose_name_plural = 'E-Invoices'

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"


class IRNAuditLog(models.Model):

    ACTION_CHOICES = [
        ('Generated', 'Generated'),
        ('Cancelled', 'Cancelled'),
        ('Failed', 'Failed'),
        ('Retried', 'Retried'),
    ]

    e_invoice  = models.ForeignKey(EInvoice, on_delete=models.CASCADE, related_name='audit_logs')
    action     = models.CharField(max_length=20, choices=ACTION_CHOICES)
    remarks    = models.TextField(blank=True, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'irn_audit_log'
        ordering = ['-performed_at']
        verbose_name = 'IRN Audit Log'
        verbose_name_plural = 'IRN Audit Logs'

    def __str__(self):
        return f"{self.e_invoice.invoice_number} - {self.action}"