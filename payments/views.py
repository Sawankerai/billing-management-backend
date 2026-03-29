from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum
from .models import Payment
from .serializers import PaymentSerializer


# --- List & Create ---
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_list(request):
    if request.method == 'GET':
        payments = Payment.objects.all().order_by('-created_at')

        search = request.query_params.get('search', '').strip()
        if search:
            payments = payments.filter(
                Q(receipt_number__icontains=search) |
                Q(customer__name__icontains=search)
            )

        gateway_status = request.query_params.get('gateway_status', '').strip()
        if gateway_status:
            payments = payments.filter(gateway_status=gateway_status)

        payment_mode = request.query_params.get('mode', '').strip()
        if payment_mode:
            payments = payments.filter(payment_mode=payment_mode)

        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Detail, Update, Delete ---
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_detail(request, pk):
    try:
        payment = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PaymentSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        payment.delete()
        return Response({"message": "Payment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# --- Apply Payment ---
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def apply_payment(request, pk):
    try:
        payment = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    if payment.status == 'Applied':
        return Response({"error": "Payment is already applied"}, status=status.HTTP_400_BAD_REQUEST)

    payment.status            = 'Applied'
    payment.gateway_status    = 'Cleared'
    payment.allocation_status = 'Allocated'
    payment.save()
    return Response({
        "message": "Payment applied successfully",
        "data": PaymentSerializer(payment).data
    }, status=status.HTTP_200_OK)


# --- Fail Payment ---
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def fail_payment(request, pk):
    try:
        payment = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    if payment.status == 'Failed':
        return Response({"error": "Payment is already failed"}, status=status.HTTP_400_BAD_REQUEST)

    payment.status         = 'Failed'
    payment.gateway_status = 'Failed'
    payment.save()
    return Response({
        "message": "Payment marked as failed",
        "data": PaymentSerializer(payment).data
    }, status=status.HTTP_200_OK)


# --- Cancel Payment ---
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def cancel_payment(request, pk):
    try:
        payment = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    if payment.status == 'Cancelled':
        return Response({"error": "Payment is already cancelled"}, status=status.HTTP_400_BAD_REQUEST)

    payment.status = 'Cancelled'
    payment.save()
    return Response({
        "message": "Payment cancelled successfully",
        "data": PaymentSerializer(payment).data
    }, status=status.HTTP_200_OK)


# --- Stats for Dashboard Cards ---
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_stats(request):
    total_receipts = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    applied = Payment.objects.filter(
        status='Applied'
    ).aggregate(total=Sum('amount'))['total'] or 0

    unapplied = Payment.objects.filter(
        status='Unapplied'
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({
        "total_receipts":  total_receipts,
        "applied":         applied,
        "unapplied":       unapplied,
        "unallocated":     Payment.objects.filter(allocation_status='Unallocated').count(),
        "failed":          Payment.objects.filter(status='Failed').count(),
        "processing":      Payment.objects.filter(status='Processing').count(),
    }, status=status.HTTP_200_OK)


# --- Payment Exceptions ---
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_exceptions(request):
    exceptions = Payment.objects.filter(
        status__in=['Failed', 'Processing']
    ).order_by('-created_at')
    serializer = PaymentSerializer(exceptions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)