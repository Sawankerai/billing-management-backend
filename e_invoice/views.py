from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from django.utils import timezone
import hashlib
import uuid

from .models import EInvoice, IRNAuditLog
from .serializers import EInvoiceSerializer, EInvoiceListSerializer


def generate_irn_number(invoice):
    raw = f"{invoice.invoice_number}-{invoice.customer_gstin}-{invoice.invoice_date}"
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_qr_code_data(invoice):
    return (
        f"IRN:{invoice.irn}|INV:{invoice.invoice_number}|"
        f"DATE:{invoice.invoice_date}|GSTIN:{invoice.customer_gstin}|"
        f"TOTAL:{invoice.total_amount}"
    )


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def einvoice_list(request):

    if request.method == 'GET':
        records = EInvoice.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            records = records.filter(
                Q(invoice_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_gstin__icontains=search) |
                Q(irn__icontains=search)
            )

        irn_status = request.query_params.get('irn_status', '').strip()
        if irn_status:
            records = records.filter(irn_status=irn_status)

        is_eligible = request.query_params.get('is_eligible', '').strip()
        if is_eligible:
            records = records.filter(is_eligible=is_eligible.lower() == 'true')

        date_from = request.query_params.get('date_from', '').strip()
        if date_from:
            records = records.filter(invoice_date__gte=date_from)

        date_to = request.query_params.get('date_to', '').strip()
        if date_to:
            records = records.filter(invoice_date__lte=date_to)

        serializer = EInvoiceListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "E-Invoice created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def einvoice_detail(request, pk):

    try:
        record = EInvoice.objects.get(pk=pk)
    except EInvoice.DoesNotExist:
        return Response({"error": "E-Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EInvoiceSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        if record.irn_status == 'Generated':
            return Response(
                {"error": "Cannot edit an invoice with a generated IRN."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EInvoiceSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "E-Invoice updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        if record.irn_status == 'Generated':
            return Response(
                {"error": "Cannot edit an invoice with a generated IRN."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EInvoiceSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "E-Invoice partially updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if record.irn_status == 'Generated':
            return Response(
                {"error": "Cannot delete an invoice with a generated IRN. Cancel it first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        record.delete()
        return Response({"message": "E-Invoice deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_irn(request, pk):

    try:
        record = EInvoice.objects.get(pk=pk)
    except EInvoice.DoesNotExist:
        return Response({"error": "E-Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

    if not record.is_eligible:
        return Response(
            {"error": "This invoice is not eligible for IRN generation."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.irn_status == 'Generated':
        return Response(
            {"error": "IRN already generated for this invoice."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.irn_status == 'Cancelled':
        return Response(
            {"error": "Cannot generate IRN for a cancelled invoice."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if EInvoice.objects.filter(invoice_number=record.invoice_number, irn_status='Generated').exclude(pk=pk).exists():
        return Response(
            {"error": "Duplicate invoice detected. IRN already exists for this invoice number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.irn = generate_irn_number(record)
    record.qr_code = generate_qr_code_data(record)
    record.irn_status = 'Generated'
    record.irn_generated_at = timezone.now()
    record.save()

    IRNAuditLog.objects.create(
        e_invoice=record,
        action='Generated',
        remarks='IRN generated successfully.'
    )

    return Response(
        {"message": "IRN generated successfully", "data": EInvoiceSerializer(record).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def cancel_irn(request, pk):

    try:
        record = EInvoice.objects.get(pk=pk)
    except EInvoice.DoesNotExist:
        return Response({"error": "E-Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

    if record.irn_status == 'Cancelled':
        return Response(
            {"error": "IRN is already cancelled."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.irn_status == 'Pending':
        return Response(
            {"error": "No IRN has been generated yet. Nothing to cancel."},
            status=status.HTTP_400_BAD_REQUEST
        )

    cancellation_reason = request.data.get('cancellation_reason', '').strip()
    if not cancellation_reason:
        return Response(
            {"error": "cancellation_reason is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.irn_status = 'Cancelled'
    record.cancellation_reason = cancellation_reason
    record.save()

    IRNAuditLog.objects.create(
        e_invoice=record,
        action='Cancelled',
        remarks=cancellation_reason
    )

    return Response(
        {"message": "IRN cancelled successfully", "data": EInvoiceSerializer(record).data},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def irn_audit_log(request, pk):

    try:
        record = EInvoice.objects.get(pk=pk)
    except EInvoice.DoesNotExist:
        return Response({"error": "E-Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

    from .serializers import IRNAuditLogSerializer
    logs = record.audit_logs.all()
    serializer = IRNAuditLogSerializer(logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def einvoice_stats(request):
    return Response({
        "eligible_invoices": EInvoice.objects.filter(is_eligible=True).count(),
        "irns_generated":    EInvoice.objects.filter(irn_status='Generated').count(),
        "pending":           EInvoice.objects.filter(irn_status='Pending').count(),
        "cancelled":         EInvoice.objects.filter(irn_status='Cancelled').count(),
    }, status=status.HTTP_200_OK)