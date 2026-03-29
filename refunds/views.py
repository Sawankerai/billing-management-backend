from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Sum

from .models import Refund
from .serializers import RefundSerializer


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def refund_list(request):
    if request.method == 'GET':
        refunds = Refund.objects.all().order_by('-created_at')

        search = request.query_params.get('search', '').strip()
        if search:
            refunds = refunds.filter(
                Q(refund_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(reference__icontains=search)
            )

        refund_status = request.query_params.get('status', '').strip()
        if refund_status:
            refunds = refunds.filter(status=refund_status)

        refund_mode = request.query_params.get('mode', '').strip()
        if refund_mode:
            refunds = refunds.filter(refund_mode=refund_mode)

        serializer = RefundSerializer(refunds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = RefundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def refund_detail(request, pk):
    try:
        refund = Refund.objects.get(pk=pk)
    except Refund.DoesNotExist:
        return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RefundSerializer(refund)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RefundSerializer(refund, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = RefundSerializer(refund, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        refund.delete()
        return Response({"message": "Refund deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def process_refund(request, pk):
    try:
        refund = Refund.objects.get(pk=pk)
    except Refund.DoesNotExist:
        return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)

    if refund.status == 'Processed':
        return Response({"error": "Refund is already processed"}, status=status.HTTP_400_BAD_REQUEST)

    if refund.status == 'Rejected':
        return Response({"error": "Cannot process a rejected refund"}, status=status.HTTP_400_BAD_REQUEST)

    if refund.status == 'Cancelled':
        return Response({"error": "Cannot process a cancelled refund"}, status=status.HTTP_400_BAD_REQUEST)

    refund.status = 'Processed'
    refund.save()
    return Response({
        "message": "Refund processed successfully",
        "data": RefundSerializer(refund).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reject_refund(request, pk):
    try:
        refund = Refund.objects.get(pk=pk)
    except Refund.DoesNotExist:
        return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)

    if refund.status == 'Rejected':
        return Response({"error": "Refund is already rejected"}, status=status.HTTP_400_BAD_REQUEST)

    if refund.status == 'Processed':
        return Response({"error": "Cannot reject an already processed refund"}, status=status.HTTP_400_BAD_REQUEST)

    refund.status = 'Rejected'
    refund.save()
    return Response({
        "message": "Refund rejected successfully",
        "data": RefundSerializer(refund).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def cancel_refund(request, pk):
    try:
        refund = Refund.objects.get(pk=pk)
    except Refund.DoesNotExist:
        return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)

    if refund.status == 'Cancelled':
        return Response({"error": "Refund is already cancelled"}, status=status.HTTP_400_BAD_REQUEST)

    refund.status = 'Cancelled'
    refund.save()
    return Response({
        "message": "Refund cancelled successfully",
        "data": RefundSerializer(refund).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def refund_stats(request):
    total_refunds = Refund.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    processed = Refund.objects.filter(
        status='Processed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending = Refund.objects.filter(
        status='Pending'
    ).aggregate(total=Sum('amount'))['total'] or 0

    rejected = Refund.objects.filter(
        status='Rejected'
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({
        "total_refunds": total_refunds,
        "processed": processed,
        "pending": pending,
        "rejected": rejected,
    }, status=status.HTTP_200_OK)