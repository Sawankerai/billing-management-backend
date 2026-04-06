from django.contrib import admin
from .models import GSTReturn, GSTReturnAuditLog


class GSTReturnAuditLogInline(admin.TabularInline):
    model        = GSTReturnAuditLog
    extra        = 0
    readonly_fields = ['action', 'remarks', 'performed_at']
    can_delete   = False


@admin.register(GSTReturn)
class GSTReturnAdmin(admin.ModelAdmin):
    list_display  = [
        'return_type',
        'period',
        'due_date',
        'filing_date',
        'status',
        'next_step',
        'arn_ack_no',
        'late_fee',
        'interest',
    ]
    list_filter   = ['status', 'return_type', 'due_date']
    search_fields = ['return_type', 'period', 'arn_ack_no']
    ordering      = ['due_date']
    readonly_fields = ['status', 'created_at', 'updated_at']
    inlines       = [GSTReturnAuditLogInline]

    fieldsets = (
        ('Return Info', {
            'fields': (
                'return_type',
                'period',
                'due_date',
                'status',
                'next_step',
            )
        }),
        ('Filing Details', {
            'fields': (
                'filing_date',
                'arn_ack_no',
                'ack_file',
                'notes',
            )
        }),
        ('Penalties', {
            'fields': (
                'late_fee',
                'interest',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )


@admin.register(GSTReturnAuditLog)
class GSTReturnAuditLogAdmin(admin.ModelAdmin):
    list_display  = ['gst_return', 'action', 'remarks', 'performed_at']
    list_filter   = ['action', 'performed_at']
    search_fields = ['gst_return__return_type', 'gst_return__period', 'remarks']
    readonly_fields = ['gst_return', 'action', 'remarks', 'performed_at']
    ordering      = ['-performed_at']