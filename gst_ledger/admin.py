from django.contrib import admin
from django.db.models import Sum
from .models import GSTLedger


@admin.register(GSTLedger)
class GSTLedgerAdmin(admin.ModelAdmin):

    list_display = (
        'date',
        'ledger_type',
        'voucher_type',
        'ref',
        'party_name',
        'debit',
        'credit',
        'cgst',
        'sgst',
        'igst',
        'is_posted',
        'created_at',
    )

    list_display_links = ('ref',)

    list_filter = (
        'ledger_type',
        'voucher_type',
        'is_posted',
        'date',
    )

    search_fields = (
        'ref',
        'party_name',
        'gstin',
        'narration',
    )

    list_editable = ('is_posted',)

    ordering = ('-date', '-created_at')

    readonly_fields = ('created_at', 'updated_at')

    list_per_page = 25

    date_hierarchy = 'date'

    fieldsets = (
        ('Ledger Info', {
            'fields': (
                'ledger_type',
                'voucher_type',
                'ref',
                'date',
                'is_posted',
            )
        }),
        ('Party Details', {
            'fields': (
                'party_name',
                'gstin',
            )
        }),
        ('Tax Amounts', {
            'fields': (
                'taxable_value',
                'cgst',
                'sgst',
                'igst',
                'cess',
                'debit',
                'credit',
            )
        }),
        ('Notes', {
            'fields': ('narration',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_posted', 'mark_unposted']

    @admin.action(description='Mark selected entries as Posted')
    def mark_posted(self, request, queryset):
        updated = queryset.update(is_posted=True)
        self.message_user(request, f'{updated} ledger entr(ies) marked as Posted.')

    @admin.action(description='Mark selected entries as Unposted')
    def mark_unposted(self, request, queryset):
        updated = queryset.update(is_posted=False)
        self.message_user(request, f'{updated} ledger entr(ies) marked as Unposted.')