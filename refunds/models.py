from django.db import models


class Refund(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processed', 'Processed'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    MODE_CHOICES = [
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Cheque', 'Cheque'),
        ('Credit Note', 'Credit Note'),
    ]

    refund_number = models.CharField(max_length=50, unique=True, editable=False)
    customer_name = models.CharField(max_length=255)
    refund_date = models.DateField()
    refund_mode = models.CharField(max_length=50, choices=MODE_CHOICES, default='Bank Transfer')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reference = models.CharField(max_length=100, blank=True, null=True)
    credit_note = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.refund_number:
            from django.utils import timezone
            today = timezone.now()
            prefix = f"RF-CN-{today.strftime('%y%m%d')}"
            last = Refund.objects.filter(
                refund_number__startswith=prefix
            ).order_by('-id').first()
            if last:
                try:
                    last_seq = int(last.refund_number.split('-')[-1])
                    seq = last_seq + 1
                except ValueError:
                    seq = 1
            else:
                seq = 1
            self.refund_number = f"{prefix}-{seq:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.refund_number} — {self.customer_name} — {self.amount}"

    class Meta:
        db_table = 'refunds'
        ordering = ['-refund_date']