from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum, Count, Max
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import SalesReport
from .serializers import SalesReportSerializer, SalesReportListSerializer


def apply_filters(queryset, request):
    search    = request.query_params.get('search', '').strip()
    customer  = request.query_params.get('customer', '').strip()
    item      = request.query_params.get('item', '').strip()
    category  = request.query_params.get('category', '').strip()
    status_v  = request.query_params.get('status', '').strip()
    date_from = request.query_params.get('from', '').strip()
    date_to   = request.query_params.get('to', '').strip()

    if search:
        queryset = queryset.filter(
            Q(invoice_no__icontains=search)    |
            Q(customer_name__icontains=search) |
            Q(company__icontains=search)       |
            Q(item__icontains=search)
        )
    if customer:
        queryset = queryset.filter(customer_name__icontains=customer)
    if item:
        queryset = queryset.filter(item__icontains=item)
    if category:
        queryset = queryset.filter(category__icontains=category)
    if status_v:
        queryset = queryset.filter(status=status_v)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    return queryset


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_report_list(request):

    if request.method == 'GET':
        records    = apply_filters(SalesReport.objects.all(), request)
        serializer = SalesReportListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SalesReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Sales record added successfully",
                 "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_report_detail(request, pk):

    try:
        record = SalesReport.objects.get(pk=pk)
    except SalesReport.DoesNotExist:
        return Response(
            {"error": "Sales record not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = SalesReportSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SalesReportSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Sales record updated successfully",
                 "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = SalesReportSerializer(
            record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Sales record partially updated",
                 "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        record.delete()
        return Response(
            {"message": "Sales record deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_summary(request):
    records = apply_filters(SalesReport.objects.all(), request)

    agg = records.aggregate(
        gross_sales_total = Sum('gross_sales'),
        returns_total     = Sum('returns'),
        tax_total         = Sum('tax'),
        paid_total        = Sum('paid'),
        count             = Count('id'),
    )

    gross_sales = agg['gross_sales_total'] or Decimal('0')
    returns     = agg['returns_total']     or Decimal('0')
    tax         = agg['tax_total']         or Decimal('0')
    collections = agg['paid_total']        or Decimal('0')
    count       = agg['count']             or 1

    net_sales   = gross_sales - returns
    outstanding = gross_sales - collections
    avg_invoice = round(gross_sales / count, 2) if count else Decimal('0')

    return Response({
        "gross_sales":       round(gross_sales, 2),
        "returns_discounts": round(returns, 2),
        "net_sales":         round(net_sales, 2),
        "tax_collected_net": round(tax, 2),
        "collections":       round(collections, 2),
        "outstanding":       round(outstanding, 2),
        "avg_invoice":       avg_invoice,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_performance(request):
    records = apply_filters(SalesReport.objects.all(), request)

    monthly = records.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        invoice_count = Count('id'),
        qty_sold      = Sum('qty_sold'),
        gross_sales   = Sum('gross_sales'),
        returns       = Sum('returns'),
        tax           = Sum('tax'),
        collections   = Sum('paid'),
    ).order_by('month')

    rows = []
    for m in monthly:
        gross     = m['gross_sales'] or Decimal('0')
        returns   = m['returns']     or Decimal('0')
        tax       = m['tax']         or Decimal('0')
        collected = m['collections'] or Decimal('0')

        rows.append({
            'period':            m['month'].strftime('%b %Y'),
            'invoices':          m['invoice_count'],
            'qty_sold':          m['qty_sold'] or 0,
            'gross_sales':       round(gross, 2),
            'returns_discounts': round(returns, 2),
            'net_sales':         round(gross - returns, 2),
            'tax_net':           round(tax, 2),
            'collections':       round(collected, 2),
            'outstanding':       round(gross - collected, 2),
        })

    return Response(rows, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def top_customers(request):
    records = apply_filters(SalesReport.objects.all(), request)

    customers = records.values(
        'customer_name', 'company'
    ).annotate(
        invoices     = Count('id'),
        gross_sales  = Sum('gross_sales'),
        returns      = Sum('returns'),
        collected    = Sum('paid'),
        last_invoice = Max('date'),
    ).order_by('-gross_sales')

    rows = []
    for c in customers:
        gross     = c['gross_sales'] or Decimal('0')
        returns   = c['returns']     or Decimal('0')
        collected = c['collected']   or Decimal('0')

        rows.append({
            'customer':     c['customer_name'],
            'company':      c['company'],
            'invoices':     c['invoices'],
            'gross_sales':  round(gross, 2),
            'returns':      round(returns, 2),
            'net_sales':    round(gross - returns, 2),
            'collected':    round(collected, 2),
            'outstanding':  round(gross - collected, 2),
            'last_invoice': c['last_invoice'],
        })

    return Response(rows, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def top_products(request):
    records = apply_filters(SalesReport.objects.all(), request)

    total_gross = records.aggregate(
        t=Sum('gross_sales'))['t'] or Decimal('1')

    products = records.values('item').annotate(
        units_sold  = Sum('qty_sold'),
        returns     = Sum('returns'),
        taxable     = Sum('taxable'),
        tax_est     = Sum('tax'),
        gross_sales = Sum('gross_sales'),
    ).order_by('-gross_sales')

    rows = []
    for p in products:
        gross   = p['gross_sales'] or Decimal('0')
        returns = p['returns']     or Decimal('0')
        share   = round((gross / total_gross) * 100, 1) if total_gross else 0

        rows.append({
            'item':        p['item'],
            'units_sold':  p['units_sold'] or 0,
            'returns':     p['returns']    or 0,
            'taxable':     round(p['taxable'] or 0, 2),
            'tax_est':     round(p['tax_est'] or 0, 2),
            'gross_sales': round(gross, 2),
            'net_sales':   round(gross - returns, 2),
            'share':       f"{share}%",
        })

    return Response(rows, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def aging_buckets(request):
    today       = timezone.now().date()
    records     = apply_filters(SalesReport.objects.all(), request)
    all_records = list(records)

    def bucket_data(filtered):
        if not filtered:
            return {
                'invoices':    0,
                'outstanding': Decimal('0'),
                'oldest_due':  None
            }
        outstanding = sum(r.outstanding for r in filtered)
        due_dates   = [r.due_date for r in filtered if r.due_date]
        return {
            'invoices':    len(filtered),
            'outstanding': round(outstanding, 2),
            'oldest_due':  min(due_dates) if due_dates else None,
        }

    current = [
        r for r in all_records
        if r.due_date and r.due_date >= today
    ]

    days_1_30 = [
        r for r in all_records
        if r.due_date
        and today - timedelta(days=30) <= r.due_date < today
    ]

    days_31_60 = [
        r for r in all_records
        if r.due_date
        and today - timedelta(days=60) <= r.due_date < today - timedelta(days=30)
    ]

    days_61_90 = [
        r for r in all_records
        if r.due_date
        and today - timedelta(days=90) <= r.due_date < today - timedelta(days=60)
    ]

    days_90p = [
        r for r in all_records
        if r.due_date
        and r.due_date < today - timedelta(days=90)
    ]

    return Response([
        {"bucket": "Current",    **bucket_data(current)},
        {"bucket": "1-30 Days",  **bucket_data(days_1_30)},
        {"bucket": "31-60 Days", **bucket_data(days_31_60)},
        {"bucket": "61-90 Days", **bucket_data(days_61_90)},
        {"bucket": "90+ Days",   **bucket_data(days_90p)},
    ], status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_register(request):
    records = apply_filters(
        SalesReport.objects.all().order_by('date'), request
    )

    rows = []
    for r in records:
        rows.append({
            'invoice':     r.invoice_no,
            'date':        r.date,
            'customer':    r.customer_name,
            'taxable':     round(r.taxable, 2),
            'tax':         round(r.tax, 2),
            'gross':       round(r.gross_sales, 2),
            'paid':        round(r.paid, 2),
            'outstanding': round(r.outstanding, 2),
        })

    return Response(rows, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_report_stats(request):
    return Response({
        "total_invoices": SalesReport.objects.count(),
        "paid":           SalesReport.objects.filter(status='paid').count(),
        "partial":        SalesReport.objects.filter(status='partial').count(),
        "outstanding":    SalesReport.objects.filter(status='outstanding').count(),
        "overdue":        SalesReport.objects.filter(status='overdue').count(),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_full_report(request):
    records = apply_filters(SalesReport.objects.all(), request)

    agg = records.aggregate(
        gross=Sum('gross_sales'),
        returns=Sum('returns'),
        tax=Sum('tax'),
        paid=Sum('paid'),
        count=Count('id'),
    )
    gross   = agg['gross']   or Decimal('0')
    returns = agg['returns'] or Decimal('0')
    tax     = agg['tax']     or Decimal('0')
    paid    = agg['paid']    or Decimal('0')
    cnt     = agg['count']   or 1

    summary = {
        "gross_sales":       round(gross, 2),
        "returns_discounts": round(returns, 2),
        "net_sales":         round(gross - returns, 2),
        "tax_collected_net": round(tax, 2),
        "collections":       round(paid, 2),
        "outstanding":       round(gross - paid, 2),
        "avg_invoice":       round(gross / cnt, 2),
    }

    monthly = records.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        invoice_count=Count('id'),
        qty_sold=Sum('qty_sold'),
        gross_sales=Sum('gross_sales'),
        returns=Sum('returns'),
        tax=Sum('tax'),
        collections=Sum('paid'),
    ).order_by('month')

    performance = [{
        'period':            m['month'].strftime('%b %Y'),
        'invoices':          m['invoice_count'],
        'qty_sold':          m['qty_sold'] or 0,
        'gross_sales':       round(m['gross_sales'] or 0, 2),
        'returns_discounts': round(m['returns'] or 0, 2),
        'net_sales':         round((m['gross_sales'] or 0) - (m['returns'] or 0), 2),
        'tax_net':           round(m['tax'] or 0, 2),
        'collections':       round(m['collections'] or 0, 2),
        'outstanding':       round((m['gross_sales'] or 0) - (m['collections'] or 0), 2),
    } for m in monthly]

    customers = records.values('customer_name', 'company').annotate(
        invoices=Count('id'),
        gross_sales=Sum('gross_sales'),
        returns=Sum('returns'),
        collected=Sum('paid'),
        last_invoice=Max('date'),
    ).order_by('-gross_sales')

    top_customers_data = [{
        'customer':     c['customer_name'],
        'company':      c['company'],
        'invoices':     c['invoices'],
        'gross_sales':  round(c['gross_sales'] or 0, 2),
        'returns':      round(c['returns'] or 0, 2),
        'net_sales':    round((c['gross_sales'] or 0) - (c['returns'] or 0), 2),
        'collected':    round(c['collected'] or 0, 2),
        'outstanding':  round((c['gross_sales'] or 0) - (c['collected'] or 0), 2),
        'last_invoice': c['last_invoice'],
    } for c in customers]

    total_gross = records.aggregate(
        t=Sum('gross_sales'))['t'] or Decimal('1')

    products = records.values('item').annotate(
        units_sold=Sum('qty_sold'),
        returns=Sum('returns'),
        taxable=Sum('taxable'),
        tax_est=Sum('tax'),
        gross_sales=Sum('gross_sales'),
    ).order_by('-gross_sales')

    top_products_data = [{
        'item':        p['item'],
        'units_sold':  p['units_sold'] or 0,
        'returns':     p['returns'] or 0,
        'taxable':     round(p['taxable'] or 0, 2),
        'tax_est':     round(p['tax_est'] or 0, 2),
        'gross_sales': round(p['gross_sales'] or 0, 2),
        'net_sales':   round((p['gross_sales'] or 0) - (p['returns'] or 0), 2),
        'share':       f"{round(((p['gross_sales'] or 0) / total_gross) * 100, 1)}%",
    } for p in products]

    register = [{
        'invoice':     r.invoice_no,
        'date':        r.date,
        'customer':    r.customer_name,
        'taxable':     round(r.taxable, 2),
        'tax':         round(r.tax, 2),
        'gross':       round(r.gross_sales, 2),
        'paid':        round(r.paid, 2),
        'outstanding': round(r.outstanding, 2),
    } for r in records.order_by('date')]

    return Response({
        'summary':       summary,
        'performance':   performance,
        'top_customers': top_customers_data,
        'top_products':  top_products_data,
        'register':      register,
    }, status=status.HTTP_200_OK)