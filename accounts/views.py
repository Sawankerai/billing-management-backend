from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum

from .models import Account
from .serializers import AccountSerializer


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def account_list(request):
    if request.method == 'GET':
        accounts = Account.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            accounts = accounts.filter(
                Q(account_name__icontains=search) |
                Q(account_code__icontains=search)
            )

        account_type = request.query_params.get('type', '').strip()
        if account_type:
            accounts = accounts.filter(account_type=account_type)

        account_status = request.query_params.get('status', '').strip()
        if account_status:
            accounts = accounts.filter(status=account_status)

        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def account_detail(request, pk):
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = AccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        account.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activate_account(request, pk):
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    if account.status == 'Active':
        return Response({"error": "Account is already active"}, status=status.HTTP_400_BAD_REQUEST)

    account.status = 'Active'
    account.save()
    return Response(
        {"message": "Account activated successfully", "data": AccountSerializer(account).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def deactivate_account(request, pk):
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

    if account.status == 'Inactive':
        return Response({"error": "Account is already inactive"}, status=status.HTTP_400_BAD_REQUEST)

    account.status = 'Inactive'
    account.save()
    return Response(
        {"message": "Account deactivated successfully", "data": AccountSerializer(account).data},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def account_stats(request):
    def total(account_type):
        result = Account.objects.filter(
            account_type=account_type, status='Active'
        ).aggregate(total=Sum('balance'))
        return result['total'] or 0

    return Response({
        "assets": total('Asset'),
        "liabilities": total('Liability'),
        "equity": total('Equity'),
        "income": total('Income'),
        "expense": total('Expense'),
        "gst_ledgers": Account.objects.filter(
            account_type='Asset',
            account_name__icontains='GST',
            status='Active'
        ).count(),
    }, status=status.HTTP_200_OK)