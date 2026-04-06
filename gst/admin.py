from django.contrib import admin
from .models import GSTRegistration


@admin.register(GSTRegistration)
class GSTRegistrationAdmin(admin.ModelAdmin):

   
    list_display = (
        'gstin',
        'legal_name',
        'trade_name',
        'state',
        'registration_type',
        'return_frequency',
        'default_gst_rate',
        'status',
        'effective_date',
        'created_at',
    )

   
    list_display_links = ('gstin', 'legal_name')

  
    list_filter = (
        'status',
        'registration_type',
        'return_frequency',
        'rounding_rule',
        'place_of_supply_rule',
        'state',
    )

   
    search_fields = (
        'gstin',
        'legal_name',
        'trade_name',
        'state',
    )

  
    list_editable = ('status',)

   
    ordering = ('-created_at',)

    
    readonly_fields = ('created_at', 'updated_at')

   
    list_per_page = 25

    # ── Detail form layout (mirrors the Add GSTIN UI screen) ──────────
    fieldsets = (
        ('GST Identity', {
            'fields': (
                'gstin',
                'legal_name',
                'trade_name',
            )
        }),
        ('Registration Details', {
            'fields': (
                'state',
                'registration_type',
                'effective_date',
                'status',
            )
        }),
        ('Tax Configuration', {
            'fields': (
                'return_frequency',
                'default_gst_rate',
                'rounding_rule',
                'place_of_supply_rule',
            )
        }),
        ('Additional Info', {
            'fields': (
                'notes',
            ),
            'classes': ('collapse',),   
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

  
    actions = ['mark_active', 'mark_inactive', 'mark_pending']

    @admin.action(description='Mark selected GSTINs as Active')
    def mark_active(self, request, queryset):
        updated = queryset.update(status='Active')
        self.message_user(request, f'{updated} GSTIN(s) marked as Active.')

    @admin.action(description='Mark selected GSTINs as Inactive')
    def mark_inactive(self, request, queryset):
        updated = queryset.update(status='Inactive')
        self.message_user(request, f'{updated} GSTIN(s) marked as Inactive.')

    @admin.action(description='Mark selected GSTINs as Pending')
    def mark_pending(self, request, queryset):
        updated = queryset.update(status='Pending')
        self.message_user(request, f'{updated} GSTIN(s) marked as Pending.')