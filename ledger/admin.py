from django.contrib import admin
from .models import Invoice, Receipt


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display  = ['invoice_number', 'customer', 'date', 'amount', 'created_at']
    search_fields = ['invoice_number', 'customer__name']
    list_filter   = ['date', 'created_at']
    ordering      = ['-created_at']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display  = ['receipt_number', 'customer', 'date', 'amount', 'created_at']
    search_fields = ['receipt_number', 'customer__name']
    list_filter   = ['date', 'created_at']
    ordering      = ['-created_at']