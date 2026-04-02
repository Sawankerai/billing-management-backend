from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from expenses.models import Expense
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth

from .serializers import (
    SummarySerializer,
    ExpensePerformanceSerializer,
    TopCategorySerializer,
    TopVendorSerializer,
    ExpenseBreakdownSerializer,
)
from decimal import Decimal



def apply_filters(queryset, request):
    category   = request.query_params.get('category')
    vendor     = request.query_params.get('vendor')
    status_val = request.query_params.get('status')
    date_from  = request.query_params.get('from')
    date_to    = request.query_params.get('to')

    if category:
        queryset = queryset.filter(category=category)
    if vendor:
        queryset = queryset.filter(vendor_payee__icontains=vendor)
    if status_val:
        queryset = queryset.filter(status=status_val)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    return queryset


# ─── Helper: compute tax from an expense queryset ────────────────────────────
def compute_tax(expense):
    """CGST + SGST for one expense object"""
    return (expense.amount * expense.cgst_rate / 100) + \
           (expense.amount * expense.sgst_rate / 100)


# ─── 1. Summary Cards ────────────────────────────────────────────────────────
@api_view(['GET'])
def report_summary(request):
    """
    GET /api/reports/summary/
    Returns: total expense, net expense, tax paid,
             approved/pending/rejected counts
    """
    expenses = apply_filters(Expense.objects.all(), request)

    net_expense  = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    approved_qs  = expenses.filter(status='approved')
    pending_qs   = expenses.filter(status='pending')
    rejected_qs  = expenses.filter(status='rejected')

    # Tax = sum of (amount * cgst_rate/100 + amount * sgst_rate/100)
    tax_paid = sum(
        compute_tax(e) for e in approved_qs
    )

    total_expense = net_expense + sum(compute_tax(e) for e in expenses)

    data = {
        'total_expense':  round(total_expense, 2),
        'net_expense':    round(net_expense, 2),
        'tax_paid':       round(tax_paid, 2),
        'approved_count': approved_qs.count(),
        'pending_count':  pending_qs.count(),
        'rejected_count': rejected_qs.count(),
    }

    serializer = SummarySerializer(data)
    return Response(serializer.data)


# ─── 2. Expense Performance (monthly table) ──────────────────────────────────
@api_view(['GET'])
def report_performance(request):
    """
    GET /api/reports/performance/
    Returns: monthly rows with expenses count, taxable,
             tax, total, approved, pending
    """
    expenses = apply_filters(Expense.objects.all(), request)

    # Group by month
    monthly = expenses.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        expense_count=Count('id'),
        taxable_sum=Sum('amount'),
        approved=Count('id', filter=Q(status='approved')),
        pending=Count('id',  filter=Q(status='pending')),
    ).order_by('month')

    rows = []
    for m in monthly:
        # Get expenses for this month to compute tax
        month_expenses = expenses.filter(
            date__year=m['month'].year,
            date__month=m['month'].month
        )
        tax   = sum(compute_tax(e) for e in month_expenses)
        total = (m['taxable_sum'] or Decimal('0')) + tax

        rows.append({
            'period':   m['month'].strftime('%b %Y'),     # Feb 2026
            'expenses': m['expense_count'],
            'taxable':  round(m['taxable_sum'] or 0, 2),
            'tax':      round(tax, 2),
            'total':    round(total, 2),
            'approved': m['approved'],
            'pending':  m['pending'],
        })

    serializer = ExpensePerformanceSerializer(rows, many=True)
    return Response(serializer.data)


# ─── 3. Top Categories ────────────────────────────────────────────────────────
@api_view(['GET'])
def report_top_categories(request):
    """
    GET /api/reports/top-categories/
    Returns: category, expenses count, tax, total — sorted by total desc
    """
    expenses = apply_filters(Expense.objects.all(), request)

    categories = expenses.values('category').annotate(
        expense_count=Count('id'),
        taxable_sum=Sum('amount'),
    ).order_by('-taxable_sum')

    rows = []
    for c in categories:
        cat_expenses = expenses.filter(category=c['category'])
        tax   = sum(compute_tax(e) for e in cat_expenses)
        total = (c['taxable_sum'] or Decimal('0')) + tax

        rows.append({
            'category': c['category'],
            'expenses': c['expense_count'],
            'tax':      round(tax, 2),
            'total':    round(total, 2),
        })

    serializer = TopCategorySerializer(rows, many=True)
    return Response(serializer.data)


# ─── 4. Top Vendors ───────────────────────────────────────────────────────────
@api_view(['GET'])
def report_top_vendors(request):
    """
    GET /api/reports/top-vendors/
    Returns: vendor, expenses count, tax, total — sorted by total desc
    """
    expenses = apply_filters(Expense.objects.all(), request)

    vendors = expenses.values('vendor_payee').annotate(
        expense_count=Count('id'),
        taxable_sum=Sum('amount'),
    ).order_by('-taxable_sum')

    rows = []
    for v in vendors:
        vendor_expenses = expenses.filter(vendor_payee=v['vendor_payee'])
        tax   = sum(compute_tax(e) for e in vendor_expenses)
        total = (v['taxable_sum'] or Decimal('0')) + tax

        rows.append({
            'vendor_payee': v['vendor_payee'],
            'expenses':     v['expense_count'],
            'tax':          round(tax, 2),
            'total':        round(total, 2),
        })

    serializer = TopVendorSerializer(rows, many=True)
    return Response(serializer.data)


# ─── 5. Expense Breakdown ─────────────────────────────────────────────────────
@api_view(['GET'])
def report_expense_breakdown(request):
    """
    GET /api/reports/breakdown/
    Returns: individual expense rows with taxable, tax, total, status
    """
    expenses = apply_filters(
        Expense.objects.all().order_by('-date'), request
    )

    rows = []
    for e in expenses:
        tax   = compute_tax(e)
        total = e.amount + tax

        rows.append({
            'date':        e.date,
            'category':    e.get_category_display(),
            'vendor_payee': e.vendor_payee,
            'taxable':     round(e.amount, 2),
            'tax':         round(tax, 2),
            'total':       round(total, 2),
            'status':      e.get_status_display(),
        })

    serializer = ExpenseBreakdownSerializer(rows, many=True)
    return Response(serializer.data)


# ─── 6. Full Report (all sections in one call) ────────────────────────────────
@api_view(['GET'])
def report_full(request):
    """
    GET /api/reports/full/
    Returns everything in one single API call
    """
    expenses = apply_filters(Expense.objects.all(), request)

    # --- Summary ---
    net_expense  = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    approved_qs  = expenses.filter(status='approved')
    pending_qs   = expenses.filter(status='pending')
    rejected_qs  = expenses.filter(status='rejected')
    all_tax      = sum(compute_tax(e) for e in expenses)
    approved_tax = sum(compute_tax(e) for e in approved_qs)

    summary = {
        'total_expense':  round(net_expense + all_tax, 2),
        'net_expense':    round(net_expense, 2),
        'tax_paid':       round(approved_tax, 2),
        'approved_count': approved_qs.count(),
        'pending_count':  pending_qs.count(),
        'rejected_count': rejected_qs.count(),
    }

    # --- Performance ---
    monthly = expenses.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        expense_count=Count('id'),
        taxable_sum=Sum('amount'),
        approved=Count('id', filter=Q(status='approved')),
        pending=Count('id',  filter=Q(status='pending')),
    ).order_by('month')

    performance = []
    for m in monthly:
        month_expenses = expenses.filter(
            date__year=m['month'].year,
            date__month=m['month'].month
        )
        tax   = sum(compute_tax(e) for e in month_expenses)
        total = (m['taxable_sum'] or Decimal('0')) + tax
        performance.append({
            'period':   m['month'].strftime('%b %Y'),
            'expenses': m['expense_count'],
            'taxable':  round(m['taxable_sum'] or 0, 2),
            'tax':      round(tax, 2),
            'total':    round(total, 2),
            'approved': m['approved'],
            'pending':  m['pending'],
        })

    # --- Top Categories ---
    cat_groups = expenses.values('category').annotate(
        expense_count=Count('id'),
        taxable_sum=Sum('amount'),
    ).order_by('-taxable_sum')

    top_categories = []
    for c in cat_groups:
        cat_expenses = expenses.filter(category=c['category'])
        tax   = sum(compute_tax(e) for e in cat_expenses)
        total = (c['taxable_sum'] or Decimal('0')) + tax
        top_categories.append({
            'category': c['category'],
            'expenses': c['expense_count'],
            'tax':      round(tax, 2),
            'total':    round(total, 2),
        })

    # --- Top Vendors ---
    vendor_groups = expenses.values('vendor_payee').annotate(
        expense_count=Count('id'),
        taxable_sum=Sum('amount'),
    ).order_by('-taxable_sum')

    top_vendors = []
    for v in vendor_groups:
        vendor_expenses = expenses.filter(vendor_payee=v['vendor_payee'])
        tax   = sum(compute_tax(e) for e in vendor_expenses)
        total = (v['taxable_sum'] or Decimal('0')) + tax
        top_vendors.append({
            'vendor_payee': v['vendor_payee'],
            'expenses':     v['expense_count'],
            'tax':          round(tax, 2),
            'total':        round(total, 2),
        })

    # --- Breakdown ---
    breakdown = []
    for e in expenses.order_by('-date'):
        tax   = compute_tax(e)
        total = e.amount + tax
        breakdown.append({
            'date':         e.date,
            'category':     e.get_category_display(),
            'vendor_payee': e.vendor_payee,
            'taxable':      round(e.amount, 2),
            'tax':          round(tax, 2),
            'total':        round(total, 2),
            'status':       e.get_status_display(),
        })

    return Response({
        'summary':        summary,
        'performance':    performance,
        'top_categories': top_categories,
        'top_vendors':    top_vendors,
        'breakdown':      breakdown,
    })