from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from .models import SalesOrder, SalesOrderItem
from .serializers import (
    SalesOrderSerializer,
    SalesOrderCreateSerializer,
    SalesOrderItemSerializer,
    ApproveOrderSerializer,
    DispatchOrderSerializer,
)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_order_list(request):
    if request.method == 'GET':
        orders = SalesOrder.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            orders = orders.filter(
                Q(so_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(company_name__icontains=search)
            )

        dispatch_status = request.query_params.get('dispatch_status', '').strip()
        if dispatch_status:
            orders = orders.filter(dispatch_status=dispatch_status)

        approval_status = request.query_params.get('approval_status', '').strip()
        if approval_status:
            orders = orders.filter(approval_status=approval_status)

        serializer = SalesOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SalesOrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                SalesOrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_order_detail(request, pk):
    try:
        order = SalesOrder.objects.get(pk=pk)
    except SalesOrder.DoesNotExist:
        return Response({"error": "Sales order not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SalesOrderSerializer(order)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SalesOrderCreateSerializer(order, data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(SalesOrderSerializer(order).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = SalesOrderCreateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save()
            return Response(SalesOrderSerializer(order).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        order.delete()
        return Response({"message": "Sales order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_order_item_list(request, pk):
    try:
        order = SalesOrder.objects.get(pk=pk)
    except SalesOrder.DoesNotExist:
        return Response({"error": "Sales order not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        items = order.items.all()
        serializer = SalesOrderItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SalesOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sales_order=order)
            order.total_items = order.items.count()
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_order_item_detail(request, pk, item_pk):
    try:
        order = SalesOrder.objects.get(pk=pk)
    except SalesOrder.DoesNotExist:
        return Response({"error": "Sales order not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        item = SalesOrderItem.objects.get(pk=item_pk, sales_order=order)
    except SalesOrderItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SalesOrderItemSerializer(item)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SalesOrderItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = SalesOrderItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item.delete()
        order.total_items = order.items.count()
        order.save()
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def approve_order(request, pk):
    try:
        order = SalesOrder.objects.get(pk=pk)
    except SalesOrder.DoesNotExist:
        return Response({"error": "Sales order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.approval_status == 'approved':
        return Response({"error": "Order is already approved"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ApproveOrderSerializer(data=request.data)
    if serializer.is_valid():
        order.approval_status = 'approved'
        if serializer.validated_data.get('notes'):
            order.notes = serializer.validated_data['notes']
        order.save()
        return Response(
            {"message": "Order approved successfully", "order": SalesOrderSerializer(order).data},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reject_order(request, pk):
    try:
        order = SalesOrder.objects.get(pk=pk)
    except SalesOrder.DoesNotExist:
        return Response({"error": "Sales order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.approval_status == 'rejected':
        return Response({"error": "Order is already rejected"}, status=status.HTTP_400_BAD_REQUEST)

    order.approval_status = 'rejected'
    order.save()
    return Response(
        {"message": "Order rejected successfully", "order": SalesOrderSerializer(order).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def dispatch_order(request, pk):
    try:
        order = SalesOrder.objects.get(pk=pk)
    except SalesOrder.DoesNotExist:
        return Response({"error": "Sales order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.approval_status != 'approved':
        return Response(
            {"error": "Order must be approved before dispatching"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = DispatchOrderSerializer(data=request.data)
    if serializer.is_valid():
        dispatched = serializer.validated_data['dispatched_items']

        if dispatched > order.total_items:
            return Response(
                {"error": f"Dispatched items cannot exceed total items ({order.total_items})"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.dispatched_items = dispatched

        if dispatched == 0:
            order.dispatch_status = 'open'
        elif dispatched < order.total_items:
            order.dispatch_status = 'partially_dispatched'
        else:
            order.dispatch_status = 'dispatched'

        if serializer.validated_data.get('notes'):
            order.notes = serializer.validated_data['notes']

        order.save()
        return Response(
            {"message": "Dispatch updated successfully", "order": SalesOrderSerializer(order).data},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_order_stats(request):
    return Response({
        "total_orders": SalesOrder.objects.count(),
        "approved": SalesOrder.objects.filter(approval_status='approved').count(),
        "pending_approval": SalesOrder.objects.filter(approval_status='pending').count(),
        "partially_dispatched": SalesOrder.objects.filter(dispatch_status='partially_dispatched').count(),
        "dispatched": SalesOrder.objects.filter(dispatch_status='dispatched').count(),
    }, status=status.HTTP_200_OK)