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
    name                = models.CharField(max_length=255)
    email               = models.EmailField(blank=True)
    phone               = models.CharField(max_length=15)
    gst_number          = models.CharField(max_length=20, blank=True)
    billing_address     = models.TextField()
    shipping_address    = models.TextField(blank=True)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    company_name = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    name         = models.CharField(max_length=200)
    email        = models.EmailField(blank=True)
    phone        = models.CharField(max_length=15)
    gst_number   = models.CharField(max_length=20, blank=True)
    bank_details = models.TextField(blank=True)

    customer_type = models.CharField(max_length=50, default='Business', blank=True)
    vendor_type = models.CharField(max_length=50, default='Supplier', blank=True)
    company_name = models.CharField(max_length=255, default='', blank=True)
    pan_no = models.CharField(max_length=20, default='', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    account_name = models.CharField(max_length=255, default='', blank=True)
    account_number = models.CharField(max_length=50, default='', blank=True)
    bank_name = models.CharField(max_length=150, default='', blank=True)
    ifsc_code = models.CharField(max_length=20, default='', blank=True)
    branch = models.CharField(max_length=150, default='', blank=True)

    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    renewal_terms = models.CharField(max_length=255, default='', blank=True)
    termination_clause = models.CharField(max_length=255, default='', blank=True)

    country = models.CharField(max_length=100, default='', blank=True)
    state = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    pin_code = models.CharField(max_length=20, default='', blank=True)
    address = models.TextField(default='', blank=True)

    @property
    def vendor_name(self):
        return self.name

    @property
    def mobile(self):
        return self.phone

    @property
    def gst_no(self):
        return self.gst_number

    def __str__(self):
        return self.name


class VendorBill(models.Model):
    BILL_TYPE_CHOICES = [
        ('GST', 'GST'),
        ('Non-GST', 'Non-GST'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Issued', 'Issued'),
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
        ('Cancelled', 'Cancelled'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='bills')
    bill_type = models.CharField(max_length=20, choices=BILL_TYPE_CHOICES, default='GST')
    date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BILL-{self.id:03d}"


class VendorBillItem(models.Model):
    bill = models.ForeignKey(VendorBill, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.item_name


class Product(models.Model):

    LOW_STOCK_THRESHOLD = 10

    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    name            = models.CharField(max_length=200)
    sku             = models.CharField(max_length=100, unique=True, blank=True, null=True)
    brand           = models.CharField(max_length=100, blank=True)
    product_code    = models.CharField(max_length=100, blank=True)
    barcode         = models.CharField(max_length=100, blank=True)
    sub_category    = models.CharField(max_length=100, blank=True)
    size            = models.CharField(max_length=50, blank=True)
    color           = models.CharField(max_length=50, blank=True)
    unit            = models.CharField(max_length=50, default='Nos', blank=True)
    tax_rate        = models.CharField(max_length=20, blank=True)
    image           = models.ImageField(upload_to='products/', blank=True, null=True)
    purchase_price  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity  = models.IntegerField(default=0)
    low_stock_limit = models.IntegerField(default=10)
    hsn_code        = models.CharField(max_length=20, blank=True)
    description     = models.TextField(blank=True)
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
    

