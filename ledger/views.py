from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum
from decimal import Decimal

from .models import Invoice, Receipt, PurchaseInvoice, SupplierPayment
from core.models import Customer, Vendor
from .serializers import CustomerSerializer, VendorSerializer, LedgerEntrySerializer



# ── Helper: Customer Ledger rows ──────────────────────────────────────────────
def build_ledger_rows(customer, from_date=None, to_date=None):
    invoice_qs = Invoice.objects.filter(customer=customer)
    receipt_qs = Receipt.objects.filter(customer=customer)

    if from_date:
        invoice_qs = invoice_qs.filter(date__gte=from_date)
        receipt_qs = receipt_qs.filter(date__gte=from_date)
    if to_date: 
        invoice_qs = invoice_qs.filter(date__lte=to_date)
        receipt_qs = receipt_qs.filter(date__lte=to_date)

    rows = []
    for inv in invoice_qs:
        rows.append({
            "date":    inv.date,
            "voucher": "Sales Invoice",
            "ref":     inv.invoice_number,
            "debit":   inv.amount,
            "credit":  Decimal("0.00"),
        })
    for rec in receipt_qs:
        rows.append({
            "date":    rec.date,
            "voucher": "Receipt",
            "ref":     rec.receipt_number,
            "debit":   Decimal("0.00"),
            "credit":  rec.amount,
        })

    rows.sort(key=lambda r: r["date"])

    opening = {
        "date":    None,
        "voucher": "Opening Balance",
        "ref":     "OPENING",
        "debit":   Decimal("0.00"),
        "credit":  Decimal("0.00"),
        "balance": Decimal("0.00"),
    }
    all_rows = [opening]
    running  = Decimal("0.00")
    for row in rows:
        running        += row["debit"] - row["credit"]
        row["balance"]  = running
        all_rows.append(row)

    return all_rows


# ── Helper: Supplier Ledger rows ──────────────────────────────────────────────
def build_supplier_ledger_rows(vendor, from_date=None, to_date=None):
    purchase_qs = PurchaseInvoice.objects.filter(vendor=vendor)
    payment_qs  = SupplierPayment.objects.filter(vendor=vendor)

    if from_date:
        purchase_qs = purchase_qs.filter(date__gte=from_date)
        payment_qs  = payment_qs.filter(date__gte=from_date)
    if to_date:
        purchase_qs = purchase_qs.filter(date__lte=to_date)
        payment_qs  = payment_qs.filter(date__lte=to_date)

    rows = []
    for inv in purchase_qs:
        rows.append({
            "date":    inv.date,
            "voucher": "Purchase Invoice",
            "ref":     inv.invoice_number,
            "debit":   inv.amount,
            "credit":  Decimal("0.00"),
        })
    for pay in payment_qs:
        rows.append({
            "date":    pay.date,
            "voucher": "Supplier Payment",
            "ref":     pay.payment_number,
            "debit":   Decimal("0.00"),
            "credit":  pay.amount,
        })

    rows.sort(key=lambda r: r["date"])

    opening = {
        "date":    None,
        "voucher": "Opening Balance",
        "ref":     "OPENING",
        "debit":   Decimal("0.00"),
        "credit":  Decimal("0.00"),
        "balance": Decimal("0.00"),
    }
    all_rows = [opening]
    running  = Decimal("0.00")
    for row in rows:
        running        += row["debit"] - row["credit"]
        row["balance"]  = running
        all_rows.append(row)

    return all_rows


# ── Customer Ledger Views ─────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_list(request):
    customers  = Customer.objects.all().order_by('name')
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ledger_entries(request):
    customer_id = request.query_params.get('customer_id', '').strip()
    from_date   = request.query_params.get('from', '').strip() or None
    to_date     = request.query_params.get('to', '').strip()   or None

    if not customer_id:
        return Response(
            {"error": "customer_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    rows       = build_ledger_rows(customer, from_date, to_date)
    serializer = LedgerEntrySerializer(rows, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ledger_stats(request):
    customer_id = request.query_params.get('customer_id', '').strip()
    from_date   = request.query_params.get('from', '').strip() or None
    to_date     = request.query_params.get('to', '').strip()   or None

    invoice_qs = Invoice.objects.all()
    receipt_qs = Receipt.objects.all()

    if customer_id:
        invoice_qs = invoice_qs.filter(customer_id=customer_id)
        receipt_qs = receipt_qs.filter(customer_id=customer_id)
    if from_date:
        invoice_qs = invoice_qs.filter(date__gte=from_date)
        receipt_qs = receipt_qs.filter(date__gte=from_date)
    if to_date:
        invoice_qs = invoice_qs.filter(date__lte=to_date)
        receipt_qs = receipt_qs.filter(date__lte=to_date)

    total_debits    = invoice_qs.aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
    total_credits   = receipt_qs.aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
    closing_balance = total_debits - total_credits

    return Response({
        "total_debits":    total_debits,
        "total_credits":   total_credits,
        "closing_balance": closing_balance,
    }, status=status.HTTP_200_OK)


# ── Supplier Ledger Views ─────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def vendor_list(request):
    vendors    = Vendor.objects.all().order_by('name')
    serializer = VendorSerializer(vendors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def supplier_ledger_entries(request):
    vendor_id = request.query_params.get('vendor_id', '').strip()
    from_date = request.query_params.get('from', '').strip() or None
    to_date   = request.query_params.get('to', '').strip()   or None

    if not vendor_id:
        return Response(
            {"error": "vendor_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        vendor = Vendor.objects.get(pk=vendor_id)
    except Vendor.DoesNotExist:
        return Response(
            {"error": "Vendor not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    rows       = build_supplier_ledger_rows(vendor, from_date, to_date)
    serializer = LedgerEntrySerializer(rows, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def supplier_ledger_stats(request):
    vendor_id = request.query_params.get('vendor_id', '').strip()
    from_date = request.query_params.get('from', '').strip() or None
    to_date   = request.query_params.get('to', '').strip()   or None

    purchase_qs = PurchaseInvoice.objects.all()
    payment_qs  = SupplierPayment.objects.all()

    if vendor_id:
        purchase_qs = purchase_qs.filter(vendor_id=vendor_id)
        payment_qs  = payment_qs.filter(vendor_id=vendor_id)
    if from_date:
        purchase_qs = purchase_qs.filter(date__gte=from_date)
        payment_qs  = payment_qs.filter(date__gte=from_date)
    if to_date:
        purchase_qs = purchase_qs.filter(date__lte=to_date)
        payment_qs  = payment_qs.filter(date__lte=to_date)

    total_debits    = purchase_qs.aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
    total_credits   = payment_qs.aggregate(total=Sum('amount'))['total']  or Decimal("0.00")
    closing_balance = total_debits - total_credits

    return Response({
        "total_debits":    total_debits,
        "total_credits":   total_credits,
        "closing_balance": closing_balance,
    }, status=status.HTTP_200_OK)

# mapping API for customer invoices

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_ledgers(request, pk):
    from django.shortcuts import get_object_or_404
    from core.models import Customer as CoreCustomer
    customer  = get_object_or_404(CoreCustomer, pk=pk)
    from_date = request.query_params.get('from', '').strip() or None
    to_date   = request.query_params.get('to', '').strip()   or None
    rows      = build_ledger_rows(customer, from_date, to_date)
    serializer = LedgerEntrySerializer(rows, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
