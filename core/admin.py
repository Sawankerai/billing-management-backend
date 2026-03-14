from django.contrib import admin
from .models import Customer, Vendor, Product, Category

admin.site.register(Customer)
admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(Category)