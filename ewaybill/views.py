from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import EWayBill, EWayBillAuditLog
from .serializers import EWayBillSerializer, EWayBillListSerializer, EWayBillAuditLogSerializer

def generate_ewaybill_number():
    """
    Generates a unique 12-digit E-Way Bill number.
    In production this would be obtained from the NIC/GST portal.
    """
    digits = ''.join(random.choices(string.digits, k=12))
    return digits

def compute_validity(distance_km: int) -> timedelta:
    """
    Returns validity period as per GST rules:
      ≤ 100 km  → 1 day
      Every additional 100 km (or part) → 1 additional day
    """
    if distance_km <= 100:
        return timedelta(days=1)
    extra = (distance_km - 100 + 99) 
    return timedelta(days=1 + extra)

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ewaybill_list(request):
   

    if request.method == 'GET':
        records = EWayBill.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            records = records.filter(
                Q(challan_number__icontains=search)  |
                Q(customer_name__icontains=search)   |
                Q(customer_gstin__icontains=search)  |
                Q(vehicle_number__icontains=search)  |
                Q(ewaybill_number__icontains=search)
            )

        ewaybill_status = request.query_params.get('ewaybill_status', '').strip()
        if ewaybill_status:
            records = records.filter(ewaybill_status=ewaybill_status)

        date_from = request.query_params.get('date_from', '').strip()
        if date_from:
            records = records.filter(challan_date__gte=date_from)

        date_to = request.query_params.get('date_to', '').strip()
        if date_to:
            records = records.filter(challan_date__lte=date_to)

        serializer = EWayBillListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EWayBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "E-Way Bill challan created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ewaybill_detail(request, pk):
    """
    GET    /ewaybills/<pk>/   → full detail
    PUT    /ewaybills/<pk>/   → full update  (blocked if Generated)
    PATCH  /ewaybills/<pk>/   → partial update (blocked if Generated)
    DELETE /ewaybills/<pk>/   → delete (blocked if Generated – cancel first)
    """

    try:
        record = EWayBill.objects.get(pk=pk)
    except EWayBill.DoesNotExist:
        return Response({"error": "E-Way Bill not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EWayBillSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ('PUT', 'PATCH'):
        if record.ewaybill_status == 'Generated':
            return Response(
                {"error": "Cannot edit a challan with a generated E-Way Bill. Cancel it first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        partial = (request.method == 'PATCH')
        serializer = EWayBillSerializer(record, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            EWayBillAuditLog.objects.create(
                e_way_bill=record,
                action='Updated',
                remarks=f"Record {'partially ' if partial else ''}updated."
            )
            verb = "partially updated" if partial else "updated"
            return Response(
                {"message": f"E-Way Bill challan {verb} successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if record.ewaybill_status == 'Generated':
            return Response(
                {"error": "Cannot delete a challan with a generated E-Way Bill. Cancel it first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        record.delete()
        return Response({"message": "E-Way Bill challan deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_ewaybill(request, pk):
   

    try:
        record = EWayBill.objects.get(pk=pk)
    except EWayBill.DoesNotExist:
        return Response({"error": "E-Way Bill not found."}, status=status.HTTP_404_NOT_FOUND)

    if record.total_value < 50000:
        return Response(
            {"error": "E-Way Bill is required only for consignments with value ≥ ₹50,000."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.ewaybill_status == 'Generated':
        return Response(
            {"error": "E-Way Bill already generated for this challan."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.ewaybill_status == 'Cancelled':
        return Response(
            {"error": "Cannot generate E-Way Bill for a cancelled challan."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.ewaybill_status == 'Closed':
        return Response(
            {"error": "Cannot re-generate E-Way Bill for a closed challan."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if EWayBill.objects.filter(
        challan_number=record.challan_number,
        ewaybill_status='Generated'
    ).exclude(pk=pk).exists():
        return Response(
            {"error": "Duplicate challan detected. E-Way Bill already exists for this challan number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    now = timezone.now()
    validity = compute_validity(record.distance_km)

    record.ewaybill_number = generate_ewaybill_number()
    record.ewaybill_status = 'Generated'
    record.generated_at    = now
    record.valid_upto      = now + validity
    record.save()

    EWayBillAuditLog.objects.create(
        e_way_bill=record,
        action='Generated',
        remarks=(
            f"E-Way Bill generated. Valid upto {record.valid_upto.strftime('%d %b %Y %H:%M')} "
            f"({validity.days} day(s) for {record.distance_km} km)."
        )
    )

    return Response(
        {"message": "E-Way Bill generated successfully.", "data": EWayBillSerializer(record).data},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def close_ewaybill(request, pk):
    """
    POST /ewaybills/<pk>/close/

    Marks a Generated E-Way Bill as Closed (e.g. on delivery confirmation).
    Optional body:
        { "remarks": "Delivered successfully." }
    """

    try:
        record = EWayBill.objects.get(pk=pk)
    except EWayBill.DoesNotExist:
        return Response({"error": "E-Way Bill not found."}, status=status.HTTP_404_NOT_FOUND)

    if record.ewaybill_status != 'Generated':
        return Response(
            {"error": f"Only a Generated E-Way Bill can be closed. Current status: {record.ewaybill_status}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    remarks = request.data.get('remarks', 'Closed on delivery confirmation.').strip()

    record.ewaybill_status = 'Closed'
    record.save()

    EWayBillAuditLog.objects.create(
        e_way_bill=record,
        action='Closed',
        remarks=remarks
    )

    return Response(
        {"message": "E-Way Bill closed successfully.", "data": EWayBillSerializer(record).data},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def cancel_ewaybill(request, pk):
   

    try:
        record = EWayBill.objects.get(pk=pk)
    except EWayBill.DoesNotExist:
        return Response({"error": "E-Way Bill not found."}, status=status.HTTP_404_NOT_FOUND)

    if record.ewaybill_status == 'Cancelled':
        return Response(
            {"error": "E-Way Bill is already cancelled."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.ewaybill_status == 'Pending':
        return Response(
            {"error": "No E-Way Bill has been generated yet. Nothing to cancel."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.ewaybill_status == 'Closed':
        return Response(
            {"error": "A closed E-Way Bill cannot be cancelled."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.generated_at and (timezone.now() - record.generated_at).total_seconds() > 86400:
        return Response(
            {"error": "E-Way Bill cannot be cancelled after 24 hours of generation."},
            status=status.HTTP_400_BAD_REQUEST
        )

    cancellation_reason = request.data.get('cancellation_reason', '').strip()
    if not cancellation_reason:
        return Response(
            {"error": "cancellation_reason is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.ewaybill_status    = 'Cancelled'
    record.cancellation_reason = cancellation_reason
    record.save()

    EWayBillAuditLog.objects.create(
        e_way_bill=record,
        action='Cancelled',
        remarks=cancellation_reason
    )

    return Response(
        {"message": "E-Way Bill cancelled successfully.", "data": EWayBillSerializer(record).data},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_vehicle(request, pk):
   

    try:
        record = EWayBill.objects.get(pk=pk)
    except EWayBill.DoesNotExist:
        return Response({"error": "E-Way Bill not found."}, status=status.HTTP_404_NOT_FOUND)

    if record.ewaybill_status != 'Generated':
        return Response(
            {"error": "Vehicle can only be updated for a Generated E-Way Bill."},
            status=status.HTTP_400_BAD_REQUEST
        )

    new_vehicle = request.data.get('vehicle_number', '').strip().upper().replace(' ', '')
    if not new_vehicle:
        return Response(
            {"error": "vehicle_number is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    import re
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$', new_vehicle):
        return Response(
            {"error": "Invalid vehicle number format. Expected format: KA01AB2034"},
            status=status.HTTP_400_BAD_REQUEST
        )

    old_vehicle = record.vehicle_number
    record.vehicle_number = new_vehicle
    record.save()

    remarks = request.data.get('remarks', f"Vehicle updated from {old_vehicle} to {new_vehicle}.").strip()
    EWayBillAuditLog.objects.create(
        e_way_bill=record,
        action='Updated',
        remarks=remarks
    )

    return Response(
        {"message": "Vehicle number updated successfully.", "data": EWayBillSerializer(record).data},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ewaybill_audit_log(request, pk):
    """
    GET /ewaybills/<pk>/audit-log/
    Returns the full audit trail for a challan.
    """

    try:
        record = EWayBill.objects.get(pk=pk)
    except EWayBill.DoesNotExist:
        return Response({"error": "E-Way Bill not found."}, status=status.HTTP_404_NOT_FOUND)

    logs = record.audit_logs.all()
    serializer = EWayBillAuditLogSerializer(logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ewaybill_stats(request):
    
    return Response({
        "challans":  EWayBill.objects.count(),
        "generated": EWayBill.objects.filter(ewaybill_status='Generated').count(),
        "pending":   EWayBill.objects.filter(ewaybill_status='Pending').count(),
        "closed":    EWayBill.objects.filter(ewaybill_status='Closed').count(),
        "cancelled": EWayBill.objects.filter(ewaybill_status='Cancelled').count(),
    }, status=status.HTTP_200_OK)