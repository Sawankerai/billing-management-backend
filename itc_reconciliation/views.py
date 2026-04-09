from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum
from django.utils import timezone

from .models import ITCReconciliation
from .serializers import (
    ITCReconciliationSerializer,
    ITCReconciliationListSerializer,
    ResolveMismatchSerializer,
)


def apply_date_filters(queryset, request):
    date_from = request.query_params.get('from', '').strip()
    date_to   = request.query_params.get('to', '').strip()
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    return queryset


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def itc_list(request):

    if request.method == 'GET':
        records = ITCReconciliation.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            records = records.filter(
                Q(expense_ref__icontains=search) |
                Q(vendor_name__icontains=search) |
                Q(vendor_gstin__icontains=search)
            )

        match_status = request.query_params.get('status', '').strip()
        if match_status:
            records = records.filter(match_status=match_status)

        eligible = request.query_params.get('eligible', '').strip()
        if eligible:
            records = records.filter(eligible=eligible)

        records = apply_date_filters(records, request)

        serializer = ITCReconciliationListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ITCReconciliationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "ITC reconciliation entry created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def itc_detail(request, pk):

    try:
        record = ITCReconciliation.objects.get(pk=pk)
    except ITCReconciliation.DoesNotExist:
        return Response(
            {"error": "ITC reconciliation entry not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = ITCReconciliationSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        if record.match_status == 'Resolved':
            return Response(
                {"error": "Cannot edit a resolved ITC entry."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ITCReconciliationSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "ITC entry updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        if record.match_status == 'Resolved':
            return Response(
                {"error": "Cannot edit a resolved ITC entry."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ITCReconciliationSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "ITC entry partially updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if record.match_status == 'Resolved':
            return Response(
                {"error": "Cannot delete a resolved ITC entry."},
                status=status.HTTP_400_BAD_REQUEST
            )
        record.delete()
        return Response(
            {"message": "ITC reconciliation entry deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def resolve_mismatch(request, pk):

    try:
        record = ITCReconciliation.objects.get(pk=pk)
    except ITCReconciliation.DoesNotExist:
        return Response(
            {"error": "ITC reconciliation entry not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if record.match_status == 'Resolved':
        return Response(
            {"error": "This ITC entry is already resolved."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.match_status == 'Matched':
        return Response(
            {"error": "This ITC entry is already matched. No resolution needed."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ResolveMismatchSerializer(data=request.data)
    if serializer.is_valid():
        record.mismatch_reason  = serializer.validated_data.get('mismatch_reason')
        record.eligible         = serializer.validated_data.get('eligible')
        record.eligible_amount  = serializer.validated_data.get('eligible_amount')
        record.resolution_notes = serializer.validated_data.get('resolution_notes', '')
        record.match_status     = 'Resolved'
        record.resolved_at      = timezone.now()

        if 'invoice_document' in request.FILES:
            record.invoice_document = request.FILES['invoice_document']

        record.save()
        return Response(
            {"message": "ITC mismatch resolved successfully", "data": ITCReconciliationSerializer(record).data},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_matched(request, pk):

    try:
        record = ITCReconciliation.objects.get(pk=pk)
    except ITCReconciliation.DoesNotExist:
        return Response(
            {"error": "ITC reconciliation entry not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if record.match_status == 'Matched':
        return Response(
            {"error": "ITC entry is already matched."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if record.match_status == 'Resolved':
        return Response(
            {"error": "Cannot mark a resolved entry as matched."},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.match_status = 'Matched'
    record.save()
    return Response(
        {"message": "ITC entry marked as matched", "data": ITCReconciliationSerializer(record).data},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def itc_stats(request):
    records = ITCReconciliation.objects.all()
    records = apply_date_filters(records, request)

    total_itc = records.filter(
        match_status='Matched'
    ).aggregate(total=Sum('tax_amount'))['total'] or 0

    return Response({
        "input_tax_credit": total_itc,
        "matched":          records.filter(match_status='Matched').count(),
        "pending":          records.filter(match_status='Pending').count(),
        "mismatched":       records.filter(match_status='Mismatch').count(),
        "resolved":         records.filter(match_status='Resolved').count(),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def itc_summary(request):
    records = ITCReconciliation.objects.all()
    records = apply_date_filters(records, request)

    matched_records   = records.filter(match_status='Matched')
    mismatch_records  = records.filter(match_status='Mismatch')
    resolved_records  = records.filter(match_status='Resolved')
    pending_records   = records.filter(match_status='Pending')

    total_tax         = records.aggregate(total=Sum('tax_amount'))['total'] or 0
    matched_tax       = matched_records.aggregate(total=Sum('tax_amount'))['total'] or 0
    mismatch_tax      = mismatch_records.aggregate(total=Sum('tax_amount'))['total'] or 0
    eligible_credit   = resolved_records.aggregate(total=Sum('eligible_amount'))['total'] or 0

    return Response({
        "total_entries":    records.count(),
        "total_tax_amount": total_tax,
        "matched": {
            "count":      matched_records.count(),
            "tax_amount": matched_tax,
        },
        "pending": {
            "count":      pending_records.count(),
            "tax_amount": pending_records.aggregate(total=Sum('tax_amount'))['total'] or 0,
        },
        "mismatch": {
            "count":      mismatch_records.count(),
            "tax_amount": mismatch_tax,
        },
        "resolved": {
            "count":          resolved_records.count(),
            "eligible_credit": eligible_credit,
        },
    }, status=status.HTTP_200_OK)