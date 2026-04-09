from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum

from .models import GSTLedger
from .serializers import GSTLedgerSerializer, GSTLedgerListSerializer


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
def gst_ledger_list(request):

    if request.method == 'GET':
        records = GSTLedger.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            records = records.filter(
                Q(ref__icontains=search) |
                Q(party_name__icontains=search) |
                Q(voucher_type__icontains=search) |
                Q(gstin__icontains=search)
            )

        ledger_type = request.query_params.get('ledger_type', '').strip()
        if ledger_type:
            records = records.filter(ledger_type=ledger_type)

        voucher_type = request.query_params.get('voucher_type', '').strip()
        if voucher_type:
            records = records.filter(voucher_type=voucher_type)

        records = apply_date_filters(records, request)

        serializer = GSTLedgerListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = GSTLedgerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "GST ledger entry created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_ledger_detail(request, pk):

    try:
        record = GSTLedger.objects.get(pk=pk)
    except GSTLedger.DoesNotExist:
        return Response(
            {"error": "GST ledger entry not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = GSTLedgerSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = GSTLedgerSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "GST ledger entry updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = GSTLedgerSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "GST ledger entry partially updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        record.delete()
        return Response(
            {"message": "GST ledger entry deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def input_gst_ledger(request):
    records = GSTLedger.objects.filter(ledger_type='Input')
    records = apply_date_filters(records, request)

    search = request.query_params.get('search', '').strip()
    if search:
        records = records.filter(
            Q(ref__icontains=search) |
            Q(party_name__icontains=search) |
            Q(voucher_type__icontains=search)
        )

    serializer = GSTLedgerListSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def output_gst_ledger(request):
    records = GSTLedger.objects.filter(ledger_type='Output')
    records = apply_date_filters(records, request)

    search = request.query_params.get('search', '').strip()
    if search:
        records = records.filter(
            Q(ref__icontains=search) |
            Q(party_name__icontains=search) |
            Q(voucher_type__icontains=search)
        )

    serializer = GSTLedgerListSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_ledger_summary(request):
    records = GSTLedger.objects.filter(is_posted=True)
    records = apply_date_filters(records, request)

    input_records  = records.filter(ledger_type='Input')
    output_records = records.filter(ledger_type='Output')

    total_input_gst  = input_records.aggregate(total=Sum('debit'))['total'] or 0
    total_output_gst = output_records.aggregate(total=Sum('credit'))['total'] or 0

    net_payable = max(total_output_gst - total_input_gst, 0)
    net_credit  = max(total_input_gst - total_output_gst, 0)

    input_cgst  = input_records.aggregate(total=Sum('cgst'))['total'] or 0
    input_sgst  = input_records.aggregate(total=Sum('sgst'))['total'] or 0
    input_igst  = input_records.aggregate(total=Sum('igst'))['total'] or 0

    output_cgst = output_records.aggregate(total=Sum('cgst'))['total'] or 0
    output_sgst = output_records.aggregate(total=Sum('sgst'))['total'] or 0
    output_igst = output_records.aggregate(total=Sum('igst'))['total'] or 0

    return Response({
        "summary_cards": {
            "input_gst":   total_input_gst,
            "output_gst":  total_output_gst,
            "net_payable": net_payable,
            "net_credit":  net_credit,
        },
        "reconciliation_summary": {
            "total_input_gst":  total_input_gst,
            "total_output_gst": total_output_gst,
            "net_payable":      net_payable,
            "net_credit":       net_credit,
        },
        "input_breakdown": {
            "cgst": input_cgst,
            "sgst": input_sgst,
            "igst": input_igst,
        },
        "output_breakdown": {
            "cgst": output_cgst,
            "sgst": output_sgst,
            "igst": output_igst,
        },
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_ledger_stats(request):
    records = GSTLedger.objects.filter(is_posted=True)

    total_input_gst  = records.filter(ledger_type='Input').aggregate(total=Sum('debit'))['total'] or 0
    total_output_gst = records.filter(ledger_type='Output').aggregate(total=Sum('credit'))['total'] or 0
    net_payable      = max(total_output_gst - total_input_gst, 0)
    net_credit       = max(total_input_gst - total_output_gst, 0)

    return Response({
        "input_gst":   total_input_gst,
        "output_gst":  total_output_gst,
        "net_payable": net_payable,
        "net_credit":  net_credit,
    }, status=status.HTTP_200_OK)