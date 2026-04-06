from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from django.utils import timezone

from .models import GSTReturn, GSTReturnAuditLog
from .serializers import (
    GSTReturnSerializer,
    GSTReturnListSerializer,
    GSTReturnUpdateStatusSerializer,
    GSTReturnAuditLogSerializer,
)


def resolve_next_step(return_type, status_value):
    if status_value == 'Filed':
        return 'Download ack' if return_type == 'GSTR-1' else 'Download challan'
    if status_value in ('Pending', 'Upcoming'):
        return f"Prepare in {return_type}"
    if status_value == 'Overdue':
        return 'Pay Late Fee'
    if status_value == 'In Review':
        return 'Under Review'
    if status_value == 'Revised':
        return 'Revised Filing'
    return None


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gstreturn_list(request):

    if request.method == 'GET':
        records = GSTReturn.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            records = records.filter(
                Q(return_type__icontains=search) |
                Q(period__icontains=search)      |
                Q(arn_ack_no__icontains=search)
            )

        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            records = records.filter(status=status_filter)

        return_type = request.query_params.get('return_type', '').strip()
        if return_type:
            records = records.filter(return_type=return_type)

        date_from = request.query_params.get('date_from', '').strip()
        if date_from:
            records = records.filter(due_date__gte=date_from)

        date_to = request.query_params.get('date_to', '').strip()
        if date_to:
            records = records.filter(due_date__lte=date_to)

        serializer = GSTReturnListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = GSTReturnSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            instance.next_step = resolve_next_step(instance.return_type, instance.status)
            instance.save()
            GSTReturnAuditLog.objects.create(
                gst_return=instance,
                action='Created',
                remarks=f"{instance.return_type} for {instance.period} created."
            )
            return Response(
                {"message": "GST Return created successfully.", "data": GSTReturnSerializer(instance).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gstreturn_detail(request, pk):

    try:
        record = GSTReturn.objects.get(pk=pk)
    except GSTReturn.DoesNotExist:
        return Response({"error": "GST Return not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GSTReturnSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ('PUT', 'PATCH'):
        if record.status == 'Filed':
            return Response(
                {"error": "Cannot edit a Filed return. Revise it first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        partial = (request.method == 'PATCH')
        serializer = GSTReturnSerializer(record, data=request.data, partial=partial)
        if serializer.is_valid():
            instance = serializer.save()
            instance.next_step = resolve_next_step(instance.return_type, instance.status)
            instance.save()
            GSTReturnAuditLog.objects.create(
                gst_return=instance,
                action='Updated',
                remarks=f"Record {'partially ' if partial else ''}updated."
            )
            verb = "partially updated" if partial else "updated"
            return Response(
                {"message": f"GST Return {verb} successfully.", "data": GSTReturnSerializer(instance).data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if record.status == 'Filed':
            return Response(
                {"error": "Cannot delete a Filed return."},
                status=status.HTTP_400_BAD_REQUEST
            )
        record.delete()
        return Response({"message": "GST Return deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_gstreturn_status(request):

    serializer = GSTReturnUpdateStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data        = serializer.validated_data
    return_type = data['return_type']
    period      = data['period']

    try:
        record = GSTReturn.objects.get(return_type=return_type, period=period)
    except GSTReturn.DoesNotExist:
        return Response(
            {"error": f"No GST Return found for {return_type} – {period}."},
            status=status.HTTP_404_NOT_FOUND
        )

    if record.status == 'Filed' and data['status'] != 'Revised':
        return Response(
            {"error": "A Filed return can only be changed to Revised."},
            status=status.HTTP_400_BAD_REQUEST
        )

    old_status = record.status

    record.status     = data['status']
    record.next_step  = resolve_next_step(return_type, data['status'])

    if data.get('filing_date'):
        record.filing_date = data['filing_date']

    if data.get('arn_ack_no'):
        record.arn_ack_no = data['arn_ack_no']

    if data.get('ack_file'):
        record.ack_file = data['ack_file']

    if data.get('notes'):
        record.notes = data['notes']

    if data.get('late_fee') is not None:
        record.late_fee = data['late_fee']

    if data.get('interest') is not None:
        record.interest = data['interest']

    record.save()

    GSTReturnAuditLog.objects.create(
        gst_return=record,
        action='Status Updated',
        remarks=f"Status changed from {old_status} to {record.status}. ARN: {record.arn_ack_no or 'N/A'}."
    )

    return Response(
        {"message": "GST Return status updated successfully.", "data": GSTReturnSerializer(record).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_overdue(request):

    today   = timezone.now().date()
    updated = GSTReturn.objects.filter(due_date__lt=today, status__in=['Pending', 'Upcoming'])
    count   = updated.count()

    for record in updated:
        old_status    = record.status
        record.status    = 'Overdue'
        record.next_step = 'Pay Late Fee'
        record.save()
        GSTReturnAuditLog.objects.create(
            gst_return=record,
            action='Overdue',
            remarks=f"Auto-marked overdue. Was {old_status}. Due date was {record.due_date}."
        )

    return Response(
        {"message": f"{count} return(s) marked as Overdue."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gstreturn_audit_log(request, pk):

    try:
        record = GSTReturn.objects.get(pk=pk)
    except GSTReturn.DoesNotExist:
        return Response({"error": "GST Return not found."}, status=status.HTTP_404_NOT_FOUND)

    logs       = record.audit_logs.all()
    serializer = GSTReturnAuditLogSerializer(logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gstreturn_stats(request):
    return Response({
        "upcoming":  GSTReturn.objects.filter(status='Upcoming').count(),
        "filed":     GSTReturn.objects.filter(status='Filed').count(),
        "overdue":   GSTReturn.objects.filter(status='Overdue').count(),
        "in_review": GSTReturn.objects.filter(status='In Review').count(),
        "pending":   GSTReturn.objects.filter(status='Pending').count(),
        "revised":   GSTReturn.objects.filter(status='Revised').count(),
    }, status=status.HTTP_200_OK)