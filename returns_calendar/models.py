from django.db import models


class GSTReturn(models.Model):

    RETURN_TYPE_CHOICES = [
        ('GSTR-1',   'GSTR-1'),
        ('GSTR-3B',  'GSTR-3B'),
        ('GSTR-2A',  'GSTR-2A'),
        ('GSTR-2B',  'GSTR-2B'),
        ('GSTR-9',   'GSTR-9'),
        ('GSTR-9C',  'GSTR-9C'),
    ]

    STATUS_CHOICES = [
        ('Upcoming',  'Upcoming'),
        ('Pending',   'Pending'),
        ('In Review', 'In Review'),
        ('Filed',     'Filed'),
        ('Overdue',   'Overdue'),
        ('Revised',   'Revised'),
    ]

    NEXT_STEP_CHOICES = [
        ('Prepare in GSTR-1',  'Prepare in GSTR-1'),
        ('Prepare in GSTR-3B', 'Prepare in GSTR-3B'),
        ('Download ack',       'Download ack'),
        ('Download challan',   'Download challan'),
        ('File Now',           'File Now'),
        ('Pay Late Fee',       'Pay Late Fee'),
        ('Under Review',       'Under Review'),
        ('Revised Filing',     'Revised Filing'),
    ]

    return_type = models.CharField(max_length=20, choices=RETURN_TYPE_CHOICES)
    period      = models.CharField(max_length=20)
    due_date    = models.DateField()
    filing_date = models.DateField(blank=True, null=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Upcoming')
    next_step   = models.CharField(max_length=50, choices=NEXT_STEP_CHOICES, blank=True, null=True)

    arn_ack_no  = models.CharField(max_length=100, blank=True, null=True)
    ack_file    = models.FileField(upload_to='gst_ack/', blank=True, null=True)
    notes       = models.TextField(blank=True, null=True)

    late_fee    = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest    = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']
        unique_together = ['return_type', 'period']

    def __str__(self):
        return f"{self.return_type} – {self.period} [{self.status}]"


class GSTReturnAuditLog(models.Model):
    gst_return   = models.ForeignKey(GSTReturn, on_delete=models.CASCADE, related_name='audit_logs')
    action       = models.CharField(max_length=50)
    remarks      = models.TextField(blank=True, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.gst_return} – {self.action}"