from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum

from .models import OpeningBalanceAccount, OpeningBalanceCustomer, TrialBalanceEntry
from .serializers import (
    OpeningBalanceAccountSerializer,
    OpeningBalanceCustomerSerializer,
    TrialBalanceEntrySerializer,
)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def trial_balance_stats(request):
    period_from = request.query_params.get('from', '').strip()
    period_to = request.query_params.get('to', '').strip()

    entries = TrialBalanceEntry.objects.all()

    if period_from:
        entries = entries.filter(period_from__gte=period_from)
    if period_to:
        entries = entries.filter(period_to__lte=period_to)

    total_debits = entries.aggregate(total=Sum('debit'))['total'] or 0
    total_credits = entries.aggregate(total=Sum('credit'))['total'] or 0
    difference = total_debits - total_credits
    accounts_count = entries.count()

    return Response({
        "total_debits": total_debits,
        "total_credits": total_credits,
        "difference": difference,
        "accounts": accounts_count,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def trial_balance_list(request):
    period_from = request.query_params.get('from', '').strip()
    period_to = request.query_params.get('to', '').strip()

    entries = TrialBalanceEntry.objects.all()

    if period_from:
        entries = entries.filter(period_from__gte=period_from)
    if period_to:
        entries = entries.filter(period_to__lte=period_to)

    account_type = request.query_params.get('type', '').strip()
    if account_type:
        entries = entries.filter(account_type=account_type)

    serializer = TrialBalanceEntrySerializer(entries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def trial_balance_entry_list(request):
    if request.method == 'GET':
        entries = TrialBalanceEntry.objects.all()
        serializer = TrialBalanceEntrySerializer(entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = TrialBalanceEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def trial_balance_entry_detail(request, pk):
    try:
        entry = TrialBalanceEntry.objects.get(pk=pk)
    except TrialBalanceEntry.DoesNotExist:
        return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TrialBalanceEntrySerializer(entry)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TrialBalanceEntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = TrialBalanceEntrySerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        entry.delete()
        return Response({"message": "Entry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def opening_balance_account_list(request):
    if request.method == 'GET':
        accounts = OpeningBalanceAccount.objects.all()
        serializer = OpeningBalanceAccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = OpeningBalanceAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def opening_balance_account_detail(request, pk):
    try:
        account = OpeningBalanceAccount.objects.get(pk=pk)
    except OpeningBalanceAccount.DoesNotExist:
        return Response({"error": "Opening balance account not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OpeningBalanceAccountSerializer(account)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OpeningBalanceAccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = OpeningBalanceAccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        account.delete()
        return Response({"message": "Opening balance account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def opening_balance_customer_list(request):
    if request.method == 'GET':
        customers = OpeningBalanceCustomer.objects.all()
        serializer = OpeningBalanceCustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = OpeningBalanceCustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def opening_balance_customer_detail(request, pk):
    try:
        customer = OpeningBalanceCustomer.objects.get(pk=pk)
    except OpeningBalanceCustomer.DoesNotExist:
        return Response({"error": "Opening balance customer not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OpeningBalanceCustomerSerializer(customer)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OpeningBalanceCustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = OpeningBalanceCustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        customer.delete()
        return Response({"message": "Opening balance customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)