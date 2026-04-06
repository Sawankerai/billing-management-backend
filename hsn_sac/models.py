from django.db import models


class HsnSac(models.Model):

    TYPE_CHOICES = [
        ('HSN', 'HSN (Goods)'),
        ('SAC', 'SAC (Services)'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Draft', 'Draft'),
        ('Inactive', 'Inactive'),
    ]

    GST_RATE_CHOICES = [
        (0, '0%'),
        (0.1, '0.1%'),
        (0.25, '0.25%'),
        (1, '1%'),
        (1.5, '1.5%'),
        (3, '3%'),
        (5, '5%'),
        (6, '6%'),
        (7.5, '7.5%'),
        (12, '12%'),
        (18, '18%'),
        (28, '28%'),
    ]

    code           = models.CharField(max_length=20, unique=True)
    type           = models.CharField(max_length=10, choices=TYPE_CHOICES)
    gst_rate       = models.DecimalField(max_digits=5, decimal_places=2, choices=GST_RATE_CHOICES)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    description    = models.TextField(blank=True, null=True)
    effective_date = models.DateField()
    map_to         = models.CharField(max_length=255, blank=True, null=True)
    notes          = models.TextField(blank=True, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hsn_sac'
        ordering = ['-created_at']
        verbose_name = 'HSN/SAC Code'
        verbose_name_plural = 'HSN/SAC Codes'

    def __str__(self):
        return f"{self.code} - {self.type}"