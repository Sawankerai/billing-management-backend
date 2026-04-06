from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from .models import HsnSac
from .serializers import HsnSacSerializer, HsnSacListSerializer


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def hsnsac_list(request):

    if request.method == 'GET':
        records = HsnSac.objects.all()

        search = request.query_params.get('search', '').strip()
        if search:
            records = records.filter(
                Q(code__icontains=search) |
                Q(description__icontains=search) |
                Q(map_to__icontains=search)
            )

        hsn_type = request.query_params.get('type', '').strip()
        if hsn_type:
            records = records.filter(type=hsn_type)

        hsn_status = request.query_params.get('status', '').strip()
        if hsn_status:
            records = records.filter(status=hsn_status)

        gst_rate = request.query_params.get('gst_rate', '').strip()
        if gst_rate:
            records = records.filter(gst_rate=gst_rate)

        serializer = HsnSacListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = HsnSacSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "HSN/SAC code added successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def hsnsac_detail(request, pk):

    try:
        record = HsnSac.objects.get(pk=pk)
    except HsnSac.DoesNotExist:
        return Response(
            {"error": "HSN/SAC code not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = HsnSacSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = HsnSacSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "HSN/SAC code updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = HsnSacSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "HSN/SAC code partially updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        record.delete()
        return Response(
            {"message": "HSN/SAC code deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activate_hsnsac(request, pk):
    try:
        record = HsnSac.objects.get(pk=pk)
    except HsnSac.DoesNotExist:
        return Response(
            {"error": "HSN/SAC code not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if record.status == 'Active':
        return Response(
            {"error": "HSN/SAC code is already active"},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.status = 'Active'
    record.save()
    return Response(
        {"message": "HSN/SAC code activated successfully", "data": HsnSacSerializer(record).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def deactivate_hsnsac(request, pk):
    try:
        record = HsnSac.objects.get(pk=pk)
    except HsnSac.DoesNotExist:
        return Response(
            {"error": "HSN/SAC code not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if record.status == 'Inactive':
        return Response(
            {"error": "HSN/SAC code is already inactive"},
            status=status.HTTP_400_BAD_REQUEST
        )

    record.status = 'Inactive'
    record.save()
    return Response(
        {"message": "HSN/SAC code deactivated successfully", "data": HsnSacSerializer(record).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def save_draft_hsnsac(request):
    data = request.data.copy()
    data['status'] = 'Draft'
    serializer = HsnSacSerializer(data=data)
    if serializer.is_valid():
        record = serializer.save()
        return Response(
            {"message": "HSN/SAC draft saved successfully", "data": HsnSacSerializer(record).data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def hsnsac_stats(request):
    return Response({
        "total_codes": HsnSac.objects.count(),
        "active":      HsnSac.objects.filter(status='Active').count(),
        "draft":       HsnSac.objects.filter(status='Draft').count(),
        "inactive":    HsnSac.objects.filter(status='Inactive').count(),
    }, status=status.HTTP_200_OK)