from django.db import models


class Category(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    name            = models.CharField(max_length=100)
    code            = models.CharField(max_length=20, unique=True, null=True, blank=True)
    description     = models.TextField(blank=True)
    image           = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name                = models.CharField(max_length=200)
    email               = models.EmailField(blank=True)
    phone               = models.CharField(max_length=15)
    gst_number          = models.CharField(max_length=20, blank=True)
    billing_address     = models.TextField()
    shipping_address    = models.TextField(blank=True)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name         = models.CharField(max_length=200)
    email        = models.EmailField(blank=True)
    phone        = models.CharField(max_length=15)
    gst_number   = models.CharField(max_length=20, blank=True)
    bank_details = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    LOW_STOCK_THRESHOLD = 10

    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    name            = models.CharField(max_length=200)
    sku             = models.CharField(max_length=100, unique=True, blank=True, null=True)
    brand           = models.CharField(max_length=100, blank=True)
    image           = models.ImageField(upload_to='products/', blank=True, null=True)
    purchase_price  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity  = models.IntegerField(default=0)
    low_stock_limit = models.IntegerField(default=10)
    hsn_code        = models.CharField(max_length=20, blank=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True, null=True)
    updated_at      = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_limit

    @property
    def is_out_of_stock(self):
        return self.stock_quantity == 0