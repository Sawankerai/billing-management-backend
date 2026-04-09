from django.contrib import admin
from .models import GSTTransaction


@admin.register(GSTTransaction)
class GSTTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number',
        'transaction_type',
        'transaction_date',
        'party_name',
        'taxable_amount',
        'cgst_amount',
        'sgst_amount',
        'igst_amount',
        'tax_rate',
        'invoice_status',
    ]
    list_filter  = [
        'transaction_type',
        'invoice_status',
        'tax_rate',
        'is_reverse_charge',
        'is_nil_exempt',
        'is_non_gst',
        'transaction_date',
    ]
    search_fields = [
        'invoice_number',
        'party_name',
        'gstin',
    ]
    ordering      = ['-transaction_date']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Transaction Info', {
            'fields': (
                'transaction_type',
                'transaction_date',
                'invoice_number',
                'invoice_status',
            )
        }),
        ('Party Details', {
            'fields': (
                'party_name',
                'gstin',
                'state_code',
            )
        }),
        ('Tax Amounts', {
            'fields': (
                'taxable_amount',
                'tax_rate',
                'cgst_amount',
                'sgst_amount',
                'igst_amount',
            )
        }),
        ('Flags', {
            'fields': (
                'is_reverse_charge',
                'is_nil_exempt',
                'is_non_gst',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )