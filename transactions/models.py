from django.db import models


class Transaction(models.Model):

    VOUCHER_TYPE_CHOICES = [
        ('Journal', 'Journal'),
        ('Receipt', 'Receipt'),
        ('Payment', 'Payment'),
        ('Contra', 'Contra'),
        ('Sales Invoice', 'Sales Invoice'),
        ('Purchase Invoice', 'Purchase Invoice'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Posted', 'Posted'),
        ('Cancelled', 'Cancelled'),
    ]

    SOURCE_CHOICES = [
        ('Auto', 'Auto'),
        ('Manual', 'Manual'),
    ]

    TAX_CHOICES = [
        ('No tax', 'No Tax'),
        ('GST 5%', 'GST 5%'),
        ('GST 12%', 'GST 12%'),
        ('GST 18%', 'GST 18%'),
        ('GST 28%', 'GST 28%'),
    ]

    voucher_number = models.CharField(max_length=50, unique=True, editable=False)
    voucher_type = models.CharField(max_length=30, choices=VOUCHER_TYPE_CHOICES, default='Journal')
    transaction_date = models.DateField()
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    debit_account = models.CharField(max_length=255)
    credit_account = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gst_tax_rate = models.CharField(max_length=20, choices=TAX_CHOICES, default='No tax')
    narration = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='Manual')
    is_tax_entry = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.voucher_number:
            from django.utils import timezone
            today = timezone.now()
            prefix_map = {
                'Journal': 'JV',
                'Receipt': 'PAY',
                'Payment': 'PMT',
                'Contra': 'CON',
                'Sales Invoice': 'INV',
                'Purchase Invoice': 'PINV',
            }
            prefix = prefix_map.get(self.voucher_type, 'TXN')
            last = Transaction.objects.filter(
                voucher_number__startswith=prefix
            ).order_by('-id').first()
            if last:
                try:
                    last_seq = int(last.voucher_number.split('-')[-1])
                    seq = last_seq + 1
                except ValueError:
                    seq = 1
            else:
                seq = 1
            self.voucher_number = f"{prefix}-{seq:04d}"

        if self.gst_tax_rate != 'No tax':
            self.is_tax_entry = True
        else:
            self.is_tax_entry = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.voucher_number} — {self.voucher_type} — {self.amount}"

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']