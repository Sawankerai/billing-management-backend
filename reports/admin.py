from django.contrib import admin
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import DecimalField, ExpressionWrapper, F
from expenses.models import Expense
from decimal import Decimal


# ─── Helper ──────────────────────────────────────────────────────────────────
def compute_tax(expense):
    return (expense.amount * expense.cgst_rate / 100) + \
           (expense.amount * expense.sgst_rate / 100)


# ─── 1. Proxy Model — Expense Summary Report ─────────────────────────────────
class ExpenseSummaryProxy(Expense):
    class Meta:
        proxy        = True
        verbose_name = 'Expense Summary Report'
        verbose_name_plural = 'Expense Summary Report'


@admin.register(ExpenseSummaryProxy)
class ExpenseSummaryAdmin(admin.ModelAdmin):

    change_list_template = 'admin/reports/summary_report.html'

    # Remove add / change / delete buttons
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        expenses     = Expense.objects.all()
        approved_qs  = expenses.filter(status='approved')
        pending_qs   = expenses.filter(status='pending')
        rejected_qs  = expenses.filter(status='rejected')

        net_expense  = expenses.aggregate(
            t=Sum('amount'))['t'] or Decimal('0')
        all_tax      = sum(compute_tax(e) for e in expenses)
        approved_tax = sum(compute_tax(e) for e in approved_qs)
        total_expense = net_expense + all_tax

        extra_context = extra_context or {}
        extra_context['summary'] = {
            'total_expense':  round(total_expense, 2),
            'net_expense':    round(net_expense, 2),
            'tax_paid':       round(approved_tax, 2),
            'approved_count': approved_qs.count(),
            'pending_count':  pending_qs.count(),
            'rejected_count': rejected_qs.count(),
        }
        return super().changelist_view(request, extra_context=extra_context)


# ─── 2. Proxy Model — Expense Performance Report ─────────────────────────────
class ExpensePerformanceProxy(Expense):
    class Meta:
        proxy        = True
        verbose_name = 'Expense Performance Report'
        verbose_name_plural = 'Expense Performance Report'


@admin.register(ExpensePerformanceProxy)
class ExpensePerformanceAdmin(admin.ModelAdmin):

    list_display = [
        'period_display',
        'expense_count_display',
        'taxable_display',
        'tax_display',
        'total_display',
        'approved_display',
        'pending_display',
    ]

    list_filter  = ['status', 'category', 'date']
    date_hierarchy = 'date'
    list_per_page  = 20

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Custom columns
    def period_display(self, obj):
        return obj.date.strftime('%b %Y')
    period_display.short_description = 'Period'

    def expense_count_display(self, obj):
        return Expense.objects.filter(
            date__year=obj.date.year,
            date__month=obj.date.month
        ).count()
    expense_count_display.short_description = 'Expenses'

    def taxable_display(self, obj):
        return format_html('₹{}', obj.amount)
    taxable_display.short_description = 'Taxable'

    def tax_display(self, obj):
        return format_html('₹{}', round(compute_tax(obj), 2))
    tax_display.short_description = 'Tax'

    def total_display(self, obj):
        return format_html('₹{}', round(obj.amount + compute_tax(obj), 2))
    total_display.short_description = 'Total'

    def approved_display(self, obj):
        color = 'green' if obj.status == 'approved' else 'gray'
        label = '✔' if obj.status == 'approved' else '–'
        return format_html(
            '<span style="color:{}">{}</span>', color, label)
    approved_display.short_description = 'Approved'

    def pending_display(self, obj):
        color = 'orange' if obj.status == 'pending' else 'gray'
        label = '⏳' if obj.status == 'pending' else '–'
        return format_html(
            '<span style="color:{}">{}</span>', color, label)
    pending_display.short_description = 'Pending'


# ─── 3. Proxy Model — Top Categories Report ──────────────────────────────────
class TopCategoryProxy(Expense):
    class Meta:
        proxy        = True
        verbose_name = 'Top Category Report'
        verbose_name_plural = 'Top Categories Report'


@admin.register(TopCategoryProxy)
class TopCategoryAdmin(admin.ModelAdmin):

    list_display = [
        'category_display',
        'expense_count_display',
        'tax_display',
        'total_display',
    ]

    list_filter  = ['category', 'status']
    list_per_page = 20

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-amount')

    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = 'Category'

    def expense_count_display(self, obj):
        return Expense.objects.filter(category=obj.category).count()
    expense_count_display.short_description = 'Expenses'

    def tax_display(self, obj):
        return format_html('₹{}', round(compute_tax(obj), 2))
    tax_display.short_description = 'Tax'

    def total_display(self, obj):
        return format_html('₹{}', round(obj.amount + compute_tax(obj), 2))
    total_display.short_description = 'Total'


# ─── 4. Proxy Model — Top Vendors Report ─────────────────────────────────────
class TopVendorProxy(Expense):
    class Meta:
        proxy        = True
        verbose_name = 'Top Vendor Report'
        verbose_name_plural = 'Top Vendors Report'


@admin.register(TopVendorProxy)
class TopVendorAdmin(admin.ModelAdmin):

    list_display = [
        'vendor_payee',
        'expense_count_display',
        'tax_display',
        'total_display',
    ]

    search_fields = ['vendor_payee']
    list_filter   = ['vendor_payee', 'status']
    list_per_page = 20

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-amount')

    def expense_count_display(self, obj):
        return Expense.objects.filter(vendor_payee=obj.vendor_payee).count()
    expense_count_display.short_description = 'Expenses'

    def tax_display(self, obj):
        return format_html('₹{}', round(compute_tax(obj), 2))
    tax_display.short_description = 'Tax'

    def total_display(self, obj):
        return format_html('₹{}', round(obj.amount + compute_tax(obj), 2))
    total_display.short_description = 'Total'


# ─── 5. Proxy Model — Expense Breakdown Report ───────────────────────────────
class ExpenseBreakdownProxy(Expense):
    class Meta:
        proxy        = True
        verbose_name = 'Expense Breakdown'
        verbose_name_plural = 'Expense Breakdown Report'


@admin.register(ExpenseBreakdownProxy)
class ExpenseBreakdownAdmin(admin.ModelAdmin):

    list_display = [
        'date',
        'category_display',
        'vendor_payee',
        'taxable_display',
        'tax_display',
        'total_display',
        'status_badge',
    ]

    list_filter = [
        'status',
        'category',
        'paid_via',
        'date',
    ]

    search_fields = [
        'vendor_payee',
        'expense_no',
        'reference',
    ]

    date_hierarchy = 'date'
    ordering       = ['-date']
    list_per_page  = 20

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = 'Category'

    def taxable_display(self, obj):
        return format_html('₹{}', obj.amount)
    taxable_display.short_description = 'Taxable'

    def tax_display(self, obj):
        return format_html('₹{}', round(compute_tax(obj), 2))
    tax_display.short_description = 'Tax'

    def total_display(self, obj):
        return format_html('₹{}', round(obj.amount + compute_tax(obj), 2))
    total_display.short_description = 'Total'

    def status_badge(self, obj):
        colors = {
            'approved': ('green',  '#e6f4ea'),
            'pending':  ('orange', '#fff4e5'),
            'rejected': ('red',    '#fce8e6'),
        }
        color, bg = colors.get(obj.status, ('gray', '#f0f0f0'))
        return format_html(
            '<span style="'
            'color:{};background:{};padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:500'
            '">{}</span>',
            color, bg, obj.get_status_display()
        )
    status_badge.short_description = 'Status'