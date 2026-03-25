from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum

from .models import Transaction
from .serializers import TransactionSerializer, SaveDraftSerializer


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    if request.method == 'GET':
        transactions = Transaction.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            transactions = transactions.filter(
                Q(voucher_number__icontains=search) |
                Q(debit_account__icontains=search) |
                Q(credit_account__icontains=search) |
                Q(reference_no__icontains=search)
            )

        voucher_type = request.query_params.get('type', '').strip()
        if voucher_type:
            transactions = transactions.filter(voucher_type=voucher_type)

        txn_status = request.query_params.get('status', '').strip()
        if txn_status:
            transactions = transactions.filter(status=txn_status)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def transaction_detail(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        transaction.delete()
        return Response({"message": "Transaction deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def save_draft(request):
    data = request.data.copy()
    data['status'] = 'Draft'
    data['source'] = 'Manual'
    serializer = SaveDraftSerializer(data=data)
    if serializer.is_valid():
        transaction = Transaction(**serializer.validated_data)
        transaction.status = 'Draft'
        transaction.source = 'Manual'
        transaction.save()
        return Response(
            {"message": "Draft saved successfully", "data": TransactionSerializer(transaction).data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def post_voucher(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    if transaction.status == 'Posted':
        return Response({"error": "Transaction is already posted"}, status=status.HTTP_400_BAD_REQUEST)

    if transaction.status == 'Cancelled':
        return Response({"error": "Cannot post a cancelled transaction"}, status=status.HTTP_400_BAD_REQUEST)

    transaction.status = 'Posted'
    transaction.save()
    return Response(
        {"message": "Voucher posted successfully", "data": TransactionSerializer(transaction).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def cancel_transaction(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    if transaction.status == 'Cancelled':
        return Response({"error": "Transaction is already cancelled"}, status=status.HTTP_400_BAD_REQUEST)

    transaction.status = 'Cancelled'
    transaction.save()
    return Response(
        {"message": "Transaction cancelled successfully", "data": TransactionSerializer(transaction).data},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def transaction_stats(request):
    posted_value = Transaction.objects.filter(
        status='Posted'
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({
        "posted_value": posted_value,
        "total_vouchers": Transaction.objects.count(),
        "pending_drafts": Transaction.objects.filter(status='Draft').count(),
        "tax_entries": Transaction.objects.filter(is_tax_entry=True).count(),
        "exceptions": Transaction.objects.filter(status='Cancelled').count(),
    }, status=status.HTTP_200_OK)