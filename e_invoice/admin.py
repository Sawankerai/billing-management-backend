from django.contrib import admin
from .models import EInvoice, IRNAuditLog


class IRNAuditLogInline(admin.TabularInline):
    model = IRNAuditLog
    extra = 0
    readonly_fields = ('action', 'remarks', 'performed_at')
    can_delete = False


@admin.register(EInvoice)
class EInvoiceAdmin(admin.ModelAdmin):

    list_display = (
        'invoice_number',
        'customer_name',
        'customer_gstin',
        'invoice_date',
        'taxable_value',
        'gst_amount',
        'total_amount',
        'irn_status',
        'is_eligible',
        'irn_generated_at',
    )

    list_display_links = ('invoice_number', 'customer_name')

    list_filter = (
        'irn_status',
        'is_eligible',
        'invoice_date',
    )

    search_fields = (
        'invoice_number',
        'customer_name',
        'customer_gstin',
        'irn',
    )

    list_editable = ('is_eligible',)

    ordering = ('-invoice_date',)

    readonly_fields = (
        'irn',
        'qr_code',
        'irn_generated_at',
        'created_at',
        'updated_at',
    )

    list_per_page = 25

    inlines = [IRNAuditLogInline]

    fieldsets = (
        ('Invoice Identity', {
            'fields': (
                'invoice_number',
                'customer_name',
                'customer_gstin',
                'invoice_date',
                'is_eligible',
            )
        }),
        ('Tax & Amount', {
            'fields': (
                'taxable_value',
                'gst_amount',
                'total_amount',
                'place_of_supply',
                'hsn_sac_code',
            )
        }),
        ('IRN Details', {
            'fields': (
                'irn_status',
                'irn',
                'qr_code',
                'irn_generated_at',
            )
        }),
        ('Cancellation & Rejection', {
            'fields': (
                'cancellation_reason',
                'rejection_reason',
            ),
            'classes': ('collapse',),
        }),
        ('Notes & Timestamps', {
            'fields': (
                'notes',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_eligible', 'mark_ineligible']

    @admin.action(description='Mark selected invoices as Eligible')
    def mark_eligible(self, request, queryset):
        updated = queryset.update(is_eligible=True)
        self.message_user(request, f'{updated} invoice(s) marked as eligible.')

    @admin.action(description='Mark selected invoices as Ineligible')
    def mark_ineligible(self, request, queryset):
        updated = queryset.update(is_eligible=False)
        self.message_user(request, f'{updated} invoice(s) marked as ineligible.')


@admin.register(IRNAuditLog)
class IRNAuditLogAdmin(admin.ModelAdmin):

    list_display = ('e_invoice', 'action', 'remarks', 'performed_at')
    list_filter  = ('action',)
    search_fields = ('e_invoice__invoice_number', 'remarks')
    readonly_fields = ('e_invoice', 'action', 'remarks', 'performed_at')
    ordering = ('-performed_at',)