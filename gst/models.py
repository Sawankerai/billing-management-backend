from django.db import models


class GSTRegistration(models.Model):

    STATE_CHOICES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Delhi', 'Delhi'),
        ('Jammu & Kashmir', 'Jammu & Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Puducherry', 'Puducherry'),
    ]

    REGISTRATION_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Composition', 'Composition'),
        ('SEZ', 'SEZ'),
        ('Casual', 'Casual'),
        ('Non-Resident', 'Non-Resident'),
        ('ISD', 'ISD'),
        ('UIN', 'UIN'),
    ]

    RETURN_FREQUENCY_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Annually', 'Annually'),
    ]

    ROUNDING_RULE_CHOICES = [
        ('Nearest', 'Nearest'),
        ('Round Up', 'Round Up'),
        ('Round Down', 'Round Down'),
    ]

    PLACE_OF_SUPPLY_RULE_CHOICES = [
        ('Ship To', 'Ship To'),
        ('Bill To', 'Bill To'),
        ('Supplier Location', 'Supplier Location'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending', 'Pending'),
        ('Inactive', 'Inactive'),
    ]

    # --- Core Fields ---
    gstin           = models.CharField(max_length=15, unique=True)
    legal_name      = models.CharField(max_length=255)
    trade_name      = models.CharField(max_length=255, blank=True, null=True)
    state           = models.CharField(max_length=100, choices=STATE_CHOICES)
    registration_type = models.CharField(
                            max_length=50,
                            choices=REGISTRATION_TYPE_CHOICES,
                            default='Regular'
                        )
    effective_date  = models.DateField()
    return_frequency = models.CharField(
                            max_length=20,
                            choices=RETURN_FREQUENCY_CHOICES,
                            default='Monthly'
                        )
    default_gst_rate = models.DecimalField(
                            max_digits=5,
                            decimal_places=2,
                            default=18.00,
                            help_text="Default GST rate in percentage"
                        )
    rounding_rule   = models.CharField(
                            max_length=20,
                            choices=ROUNDING_RULE_CHOICES,
                            default='Nearest'
                        )
    place_of_supply_rule = models.CharField(
                            max_length=50,
                            choices=PLACE_OF_SUPPLY_RULE_CHOICES,
                            default='Ship To'
                        )
    notes           = models.TextField(blank=True, null=True)
    status          = models.CharField(
                            max_length=20,
                            choices=STATUS_CHOICES,
                            default='Pending'
                        )

    # --- Timestamps ---
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gst_registration'
        ordering = ['-created_at']
        verbose_name = 'GST Registration'
        verbose_name_plural = 'GST Registrations'

    def __str__(self):
        return f"{self.gstin} - {self.legal_name}"