from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    # Columns shown in the list view
    list_display = [
        'expense_no',
        'category',
        'date',
        'vendor_payee',
        'amount',
        'cgst_rate',
        'sgst_rate',
        'paid_via',
        'status',
        'reference',
        'created_at',
    ]

    # Clickable link column
    list_display_links = ['expense_no']

    # Filter sidebar on the right
    list_filter = [
        'status',
        'category',
        'paid_via',
        'date',
    ]

    # Search bar
    search_fields = [
        'expense_no',
        'vendor_payee',
        'reference',
        'notes',
    ]

    # Inline editable fields directly in list view
    list_editable = [
        'status',
    ]

    # Default ordering — newest date first
    ordering = ['-date']

    # Records per page
    list_per_page = 20

    # Date drill-down navigation at the top
    date_hierarchy = 'date'

    # Group fields into sections in the detail/edit form
    fieldsets = (
        ('Expense Info', {
            'fields': (
                'expense_no',
                'category',
                'date',
                'vendor_payee',
            )
        }),
        ('Amount & Tax', {
            'fields': (
                'amount',
                'cgst_rate',
                'sgst_rate',
            ),
            'description': 'Enter base amount. GST is calculated automatically.'
        }),
        ('Payment', {
            'fields': (
                'paid_via',
                'status',
                'reference',
            )
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',),    # collapsed by default
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    # Auto-generated and auto-filled fields — read only in admin
    readonly_fields = [
        'expense_no',
        'created_at',
        'updated_at',
    ]

    # Show computed GST summary in the list view
    def cgst_amount_display(self, obj):
        return f"₹{obj.cgst_amount}"
    cgst_amount_display.short_description = 'CGST Amount'

    def sgst_amount_display(self, obj):
        return f"₹{obj.sgst_amount}"
    sgst_amount_display.short_description = 'SGST Amount'

    def total_amount_display(self, obj):
        return f"₹{obj.total_amount}"
    total_amount_display.short_description = 'Total (incl. GST)'

    # Add computed columns to list view
    list_display = [
        'expense_no',
        'category',
        'date',
        'vendor_payee',
        'amount',
        'cgst_amount_display',
        'sgst_amount_display',
        'total_amount_display',
        'paid_via',
        'status',
        'reference',
        'created_at',
    ]