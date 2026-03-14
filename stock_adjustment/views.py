from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import StockAdjustment
from .serializers import StockAdjustmentSerializer


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def adjustment_list(request):
    if request.method == 'GET':
        adjustments = StockAdjustment.objects.all()
        serializer = StockAdjustmentSerializer(adjustments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = StockAdjustmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def adjustment_detail(request, pk):
    try:
        adjustment = StockAdjustment.objects.get(pk=pk)
    except StockAdjustment.DoesNotExist:
        return Response({"error": "Stock Adjustment not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StockAdjustmentSerializer(adjustment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StockAdjustmentSerializer(adjustment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = StockAdjustmentSerializer(adjustment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        adjustment.delete()
        return Response({"message": "Stock Adjustment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def adjustment_save_draft(request):
    data = request.data.copy()
    data['status'] = 'Draft'
    serializer = StockAdjustmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Draft saved", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def adjustment_stats(request):
    from core.models import Product

    recent_adjustments = StockAdjustment.objects.count()
    damaged_stock      = StockAdjustment.objects.filter(adjustment_type='Damaged').count()
    low_stock          = Product.objects.filter(
        stock_quantity__lte=10,
        stock_quantity__gt=0
    ).count()

    return Response({
        "recent_adjustments": recent_adjustments,
        "damaged_stock":      damaged_stock,
        "low_stock":          low_stock,
    }, status=status.HTTP_200_OK)