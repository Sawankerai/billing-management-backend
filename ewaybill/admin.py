from django.contrib import admin
from .models import EWayBill, EWayBillAuditLog


class EWayBillAuditLogInline(admin.TabularInline):
    model = EWayBillAuditLog
    extra = 0
    readonly_fields = ['action', 'remarks', 'performed_at']
    can_delete = False


@admin.register(EWayBill)
class EWayBillAdmin(admin.ModelAdmin):
    list_display = [
        'challan_number',
        'customer_name',
        'challan_date',
        'vehicle_number',
        'total_value',
        'ewaybill_status',
        'ewaybill_number',
        'valid_upto',
    ]
    list_filter = ['ewaybill_status', 'challan_date']
    search_fields = [
        'challan_number',
        'customer_name',
        'customer_gstin',
        'vehicle_number',
        'ewaybill_number',
    ]
    readonly_fields = [
        'ewaybill_number',
        'ewaybill_status',
        'generated_at',
        'valid_upto',
        'cancellation_reason',
        'created_at',
        'updated_at',
    ]
    ordering = ['-challan_date']
    inlines = [EWayBillAuditLogInline]

    fieldsets = (
        ('Challan Info', {
            'fields': (
                'challan_number',
                'invoice_number',
                'challan_date',
            )
        }),
        ('Customer', {
            'fields': (
                'customer_name',
                'customer_gstin',
            )
        }),
        ('Transport', {
            'fields': (
                'vehicle_number',
                'transporter_id',
                'transporter_name',
                'from_place',
                'to_place',
                'distance_km',
            )
        }),
        ('Value', {
            'fields': (
                'total_value',
            )
        }),
        ('E-Way Bill', {
            'fields': (
                'ewaybill_number',
                'ewaybill_status',
                'generated_at',
                'valid_upto',
                'cancellation_reason',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )


@admin.register(EWayBillAuditLog)
class EWayBillAuditLogAdmin(admin.ModelAdmin):
    list_display = ['e_way_bill', 'action', 'remarks', 'performed_at']
    list_filter = ['action', 'performed_at']
    search_fields = ['e_way_bill__challan_number', 'remarks']
    readonly_fields = ['e_way_bill', 'action', 'remarks', 'performed_at']
    ordering = ['-performed_at']