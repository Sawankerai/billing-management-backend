from django.contrib import admin
from .models import RecurringExpense


@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):

   
    list_display = [
        'template_name',
        'category',
        'frequency',
        'next_run',
        'amount',
        'status',
        'vendor_payee',
        'auto_post_ledger',
        'notify_before_run',
        'created_at',
    ]

    # Clickable link column
    list_display_links = ['template_name']

    # Filter sidebar on the right
    list_filter = [
        'status',
        'frequency',
        'category',
        'auto_post_ledger',
        'notify_before_run',
    ]

    # Search bar
    search_fields = [
        'template_name',
        'vendor_payee',
        'notes',
    ]

    # Inline editable fields directly in list view
    list_editable = [
        'status',
        'amount',
    ]

    # Default ordering
    ordering = ['next_run']

    # How many records per page
    list_per_page = 20

    # Group fields into sections in the detail/edit form
    fieldsets = (
        ('Template Info', {
            'fields': (
                'template_name',
                'category',
                'vendor_payee',
            )
        }),
        ('Schedule', {
            'fields': (
                'frequency',
                'next_run',
                'amount',
                'status',
            )
        }),
        ('Controls', {
            'fields': (
                'auto_post_ledger',
                'notify_before_run',
            )
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',),   # collapsed by default
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    # These fields are auto-filled, make them read-only in admin
    readonly_fields = ['created_at', 'updated_at']

    # Date drill-down navigation at the top
    date_hierarchy = 'next_run'