from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Q

from .models import BarcodeDevice, StockMovement
from .serializers import (
    BarcodeDeviceSerializer,
    StockMovementSerializer,
    BarcodeScanSerializer,
    CreateTransferSerializer,
)

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def device_list(request):
   
    if request.method == 'GET':
        devices = BarcodeDevice.objects.all()
        serializer = BarcodeDeviceSerializer(devices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = BarcodeDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def device_detail(request, pk):
   
    try:
        device = BarcodeDevice.objects.get(pk=pk)
    except BarcodeDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BarcodeDeviceSerializer(device)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BarcodeDeviceSerializer(device, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = BarcodeDeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        device.delete()
        return Response({"message": "Device removed successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def device_connect(request, pk):
   
    try:
        device = BarcodeDevice.objects.get(pk=pk)
    except BarcodeDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    device.status = 'connected'
    device.save()
    serializer = BarcodeDeviceSerializer(device)
    return Response({"message": "Device connected", "device": serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def device_disconnect(request, pk):
   
    try:
        device = BarcodeDevice.objects.get(pk=pk)
    except BarcodeDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    device.status = 'disconnected'
    device.save()
    serializer = BarcodeDeviceSerializer(device)
    return Response({"message": "Device disconnected", "device": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def movement_list(request):
    
    movements = StockMovement.objects.all()

    search = request.query_params.get('search', '').strip()
    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(sku__icontains=search) |
            Q(product_name__icontains=search) |
            Q(reference__icontains=search)
        )

    movement_status = request.query_params.get('status', '').strip()
    if movement_status:
        movements = movements.filter(status=movement_status)

    movement_type = request.query_params.get('type', '').strip()
    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    serializer = StockMovementSerializer(movements, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def movement_detail(request, pk):
    
    try:
        movement = StockMovement.objects.get(pk=pk)
    except StockMovement.DoesNotExist:
        return Response({"error": "Stock movement not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StockMovementSerializer(movement)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StockMovementSerializer(movement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = StockMovementSerializer(movement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        movement.delete()
        return Response({"message": "Stock movement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def barcode_scan(request):
   
    serializer = BarcodeScanSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    device = None

    if data.get('device_id'):
        try:
            device = BarcodeDevice.objects.get(pk=data['device_id'])
            device.last_scan_barcode = data['barcode']
            device.last_scan_at = timezone.now()
            device.save()
        except BarcodeDevice.DoesNotExist:
            pass

    movement = StockMovement.objects.create(
        movement_type=data['scan_mode'],
        barcode=data['barcode'],
        sku=data['sku'],
        product_name=data['product_name'],
        quantity=data['quantity'],
        from_location=data.get('from_location', ''),
        to_location=data['to_location'],
        reference=data.get('reference', ''),
        status='posted',
        device=device,
        scanned_at=timezone.now(),
    )

    return Response(
        {
            "message": "Scan recorded successfully",
            "movement": StockMovementSerializer(movement).data,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_transfer(request):
    
    serializer = CreateTransferSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    device = None

    if data.get('device_id'):
        try:
            device = BarcodeDevice.objects.get(pk=data['device_id'])
        except BarcodeDevice.DoesNotExist:
            pass

    movement = StockMovement.objects.create(
        movement_type='transfer',
        sku=data['sku'],
        product_name=data['product_name'],
        quantity=data['quantity'],
        from_location=data['from_location'],
        to_location=data['to_location'],
        reference=data.get('reference', ''),
        status='in_transit',
        device=device,
        scanned_at=timezone.now(),
    )

    return Response(
        {
            "message": "Transfer created successfully",
            "movement": StockMovementSerializer(movement).data,
        },
        status=status.HTTP_201_CREATED,
    )




@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def export_movement_log(request):
    
    movements = StockMovement.objects.all()

    search = request.query_params.get('search', '').strip()
    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(sku__icontains=search) |
            Q(product_name__icontains=search) |
            Q(reference__icontains=search)
        )

    movement_status = request.query_params.get('status', '').strip()
    if movement_status:
        movements = movements.filter(status=movement_status)

    movement_type = request.query_params.get('type', '').strip()
    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    serializer = StockMovementSerializer(movements, many=True)
    return Response(
        {
            "total": movements.count(),
            "movements": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
