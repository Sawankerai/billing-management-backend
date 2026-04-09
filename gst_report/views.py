from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum, Value
from django.db.models.functions import TruncMonth
from django.db.models import DecimalField
from django.db.models.functions import Coalesce

from .models import GSTTransaction
from .serializers import GSTTransactionSerializer, GSTTransactionListSerializer

ZERO = Value(0, output_field=DecimalField())


def apply_filters(queryset, request):
    search = request.query_params.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(invoice_number__icontains=search) |
            Q(party_name__icontains=search)     |
            Q(gstin__icontains=search)
        )

    invoice_status = request.query_params.get('invoice_status', '').strip()
    if invoice_status:
        queryset = queryset.filter(invoice_status=invoice_status)

    date_from = request.query_params.get('from', '').strip()
    if date_from:
        queryset = queryset.filter(transaction_date__gte=date_from)

    date_to = request.query_params.get('to', '').strip()
    if date_to:
        queryset = queryset.filter(transaction_date__lte=date_to)

    gstin = request.query_params.get('gstin', '').strip()
    if gstin:
        queryset = queryset.filter(gstin__icontains=gstin)

    tax_rate = request.query_params.get('tax_rate', '').strip()
    if tax_rate:
        queryset = queryset.filter(tax_rate=tax_rate)

    state_code = request.query_params.get('state_code', '').strip()
    if state_code:
        queryset = queryset.filter(state_code=state_code)

    return queryset


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_transaction_list(request):

    if request.method == 'GET':
        records = GSTTransaction.objects.all()
        records = apply_filters(records, request)

        transaction_type = request.query_params.get('type', '').strip()
        if transaction_type:
            records = records.filter(transaction_type=transaction_type)

        serializer = GSTTransactionListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = GSTTransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "GST transaction created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_transaction_detail(request, pk):

    try:
        record = GSTTransaction.objects.get(pk=pk)
    except GSTTransaction.DoesNotExist:
        return Response({"error": "GST transaction not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GSTTransactionSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ('PUT', 'PATCH'):
        if record.invoice_status == 'Cancelled':
            return Response(
                {"error": "Cannot edit a cancelled transaction."},
                status=status.HTTP_400_BAD_REQUEST
            )
        partial = (request.method == 'PATCH')
        serializer = GSTTransactionSerializer(record, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            verb = "partially updated" if partial else "updated"
            return Response(
                {"message": f"GST transaction {verb} successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if record.invoice_status == 'Cancelled':
            return Response(
                {"error": "Cannot delete a cancelled transaction."},
                status=status.HTTP_400_BAD_REQUEST
            )
        record.delete()
        return Response({"message": "GST transaction deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_summary(request):

    all_records = GSTTransaction.objects.exclude(invoice_status='Cancelled')
    all_records = apply_filters(all_records, request)

    output = all_records.filter(transaction_type='Output')
    input_ = all_records.filter(transaction_type='Input')
    returns = all_records.filter(transaction_type='Output', invoice_status='Returns')

    def agg(qs):
        return qs.aggregate(
            taxable=Coalesce(Sum('taxable_amount'), ZERO),
            cgst=Coalesce(Sum('cgst_amount'), ZERO),
            sgst=Coalesce(Sum('sgst_amount'), ZERO),
            igst=Coalesce(Sum('igst_amount'), ZERO),
        )

    out_agg  = agg(output)
    in_agg   = agg(input_)
    ret_agg  = agg(returns)

    output_tax  = out_agg['cgst'] + out_agg['sgst'] + out_agg['igst']
    input_tax   = in_agg['cgst']  + in_agg['sgst']  + in_agg['igst']
    returns_tax = ret_agg['cgst'] + ret_agg['sgst']  + ret_agg['igst']
    net_output  = output_tax - returns_tax
    net_payable = net_output - input_tax

    cgst_out = out_agg['cgst'] - ret_agg['cgst']
    sgst_out = out_agg['sgst'] - ret_agg['sgst']
    igst_out = out_agg['igst'] - ret_agg['igst']

    cgst_in  = in_agg['cgst']
    sgst_in  = in_agg['sgst']
    igst_in  = in_agg['igst']

    return Response({
        "dashboard": {
            "taxable_turnover": out_agg['taxable'],
            "output_tax":       output_tax,
            "returns_tax":      returns_tax,
            "input_tax_credit": input_tax,
            "net_output_tax":   net_output,
            "net_gst_payable":  net_payable,
        },
        "tax_type_breakup": [
            {
                "tax_type":   "CGST",
                "output_tax": cgst_out,
                "input_tax":  cgst_in,
                "net":        cgst_out - cgst_in,
            },
            {
                "tax_type":   "SGST",
                "output_tax": sgst_out,
                "input_tax":  sgst_in,
                "net":        sgst_out - sgst_in,
            },
            {
                "tax_type":   "IGST",
                "output_tax": igst_out,
                "input_tax":  igst_in,
                "net":        igst_out - igst_in,
            },
            {
                "tax_type":   "Total",
                "output_tax": cgst_out + sgst_out + igst_out,
                "input_tax":  cgst_in  + sgst_in  + igst_in,
                "net":        net_output - input_tax,
            },
        ],
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def monthly_gst_position(request):

    records = GSTTransaction.objects.exclude(invoice_status='Cancelled')
    records = apply_filters(records, request)

    output  = records.filter(transaction_type='Output')
    input_  = records.filter(transaction_type='Input')
    returns = records.filter(transaction_type='Output', invoice_status='Returns')

    def monthly_agg(qs):
        return qs.annotate(period=TruncMonth('transaction_date')).values('period').annotate(
            cgst=Coalesce(Sum('cgst_amount'), ZERO),
            sgst=Coalesce(Sum('sgst_amount'), ZERO),
            igst=Coalesce(Sum('igst_amount'), ZERO),
        ).order_by('period')

    out_monthly = {r['period']: r for r in monthly_agg(output)}
    in_monthly  = {r['period']: r for r in monthly_agg(input_)}
    ret_monthly = {r['period']: r for r in monthly_agg(returns)}

    all_periods = sorted(set(out_monthly) | set(in_monthly))

    result = []
    for period in all_periods:
        o = out_monthly.get(period, {'cgst': 0, 'sgst': 0, 'igst': 0})
        i = in_monthly.get(period, {'cgst': 0, 'sgst': 0, 'igst': 0})
        r = ret_monthly.get(period, {'cgst': 0, 'sgst': 0, 'igst': 0})

        out_tax  = o['cgst'] + o['sgst'] + o['igst']
        ret_tax  = r['cgst'] + r['sgst'] + r['igst']
        in_tax   = i['cgst'] + i['sgst'] + i['igst']
        net      = out_tax - ret_tax - in_tax

        result.append({
            "period":       period.strftime('%b %Y'),
            "output_tax":   out_tax,
            "returns_tax":  ret_tax,
            "input_tax":    in_tax,
            "net_payable":  net,
        })

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_slab_breakup(request):

    records = GSTTransaction.objects.exclude(invoice_status='Cancelled')
    records = apply_filters(records, request)

    slabs = records.values('tax_rate').annotate(
        taxable_amount=Coalesce(Sum('taxable_amount'), ZERO),
        tax_amount=Coalesce(
            Sum('cgst_amount') + Sum('sgst_amount') + Sum('igst_amount'),
            ZERO
        ),
    ).order_by('tax_rate')

    result = [
        {
            "tax_rate":      f"{s['tax_rate']}%",
            "taxable_amount": s['taxable_amount'],
            "tax_amount":     s['tax_amount'],
        }
        for s in slabs
    ]

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gstr3b_mapping(request):

    records = GSTTransaction.objects.exclude(invoice_status='Cancelled')
    records = apply_filters(records, request)

    output  = records.filter(transaction_type='Output')
    input_  = records.filter(transaction_type='Input')

    def total_tax(qs):
        r = qs.aggregate(
            cgst=Coalesce(Sum('cgst_amount'), ZERO),
            sgst=Coalesce(Sum('sgst_amount'), ZERO),
            igst=Coalesce(Sum('igst_amount'), ZERO),
            taxable=Coalesce(Sum('taxable_amount'), ZERO),
        )
        return r

    outward_taxable  = total_tax(output.filter(is_nil_exempt=False, is_non_gst=False, is_reverse_charge=False))
    nil_exempt       = total_tax(output.filter(is_nil_exempt=True))
    reverse_charge   = total_tax(output.filter(is_reverse_charge=True))
    non_gst          = total_tax(output.filter(is_non_gst=True))
    eligible_itc     = total_tax(input_.filter(is_reverse_charge=False))
    ineligible_itc   = total_tax(input_.filter(is_reverse_charge=True))

    def tax_sum(r):
        return r['cgst'] + r['sgst'] + r['igst']

    out_tax_total = tax_sum(outward_taxable)
    itc_total     = tax_sum(eligible_itc)
    net_payable   = out_tax_total - itc_total

    return Response([
        {
            "section":        "3.1(a) Outward taxable supplies",
            "taxable_value":  outward_taxable['taxable'],
            "tax_amount":     out_tax_total,
        },
        {
            "section":        "3.1(c) Other outward supplies (nil/exempt)",
            "taxable_value":  nil_exempt['taxable'],
            "tax_amount":     tax_sum(nil_exempt),
        },
        {
            "section":        "3.1(d) Inward supplies (reverse charge)",
            "taxable_value":  reverse_charge['taxable'],
            "tax_amount":     tax_sum(reverse_charge),
        },
        {
            "section":        "3.1(e) Non-GST outward supplies",
            "taxable_value":  non_gst['taxable'],
            "tax_amount":     tax_sum(non_gst),
        },
        {
            "section":        "4(A) Eligible ITC (Input tax)",
            "taxable_value":  eligible_itc['taxable'],
            "tax_amount":     itc_total,
        },
        {
            "section":        "4(B) Ineligible ITC",
            "taxable_value":  ineligible_itc['taxable'],
            "tax_amount":     tax_sum(ineligible_itc),
        },
        {
            "section":        "Net GST Payable",
            "taxable_value":  0,
            "tax_amount":     net_payable,
        },
    ], status=status.HTTP_200_OK)