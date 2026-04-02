from django.db import models

class RecurringExpense(models.Model):

    FREQUENCY_CHOICES = [
        ('daily',     'Daily'),
        ('weekly',    'Weekly'),
        ('monthly',   'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly',    'Yearly'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('due_soon', 'Due Soon'),
    ]

    CATEGORY_CHOICES = [
        ('rent_utilities',    'Rent & Utilities'),
        ('it_software',       'IT & Software'),
        ('legal_compliance',  'Legal & Compliance'),
        ('travel_transport',  'Travel & Transport'),
        ('office_supplies',   'Office Supplies'),
        ('marketing_ads',     'Marketing & Ads'),
    ]

    template_name = models.CharField(max_length=200)          
    category      = models.CharField(max_length=50,
                        choices=CATEGORY_CHOICES)              
    frequency     = models.CharField(max_length=20,
                        choices=FREQUENCY_CHOICES)             
    next_run      = models.DateField()                         
    amount        = models.DecimalField(max_digits=12,
                        decimal_places=2)                      
    status        = models.CharField(max_length=20,
                        choices=STATUS_CHOICES,
                        default='active')                      
    vendor_payee  = models.CharField(max_length=200,
                        blank=True)                           
    notes         = models.TextField(blank=True)               
    auto_post_ledger   = models.BooleanField(default=True)     
    notify_before_run  = models.BooleanField(default=True)     
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template_name} ({self.frequency})"

    class Meta:
        ordering = ['next_run']