from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from .models import GSTRegistration
from .serializers import GSTRegistrationSerializer, GSTRegistrationListSerializer

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_list(request):

    if request.method == 'GET':
        gst_records = GSTRegistration.objects.all()

        # Search across GSTIN, legal name, trade name, state
        search = request.query_params.get('search', '').strip()
        if search:
            gst_records = gst_records.filter(
                Q(gstin__icontains=search) |
                Q(legal_name__icontains=search) |
                Q(trade_name__icontains=search) |
                Q(state__icontains=search)
            )

        # Filter by registration type (Regular / Composition / SEZ …)
        reg_type = request.query_params.get('type', '').strip()
        if reg_type:
            gst_records = gst_records.filter(registration_type=reg_type)

        # Filter by status (Active / Pending / Inactive)
        gst_status = request.query_params.get('status', '').strip()
        if gst_status:
            gst_records = gst_records.filter(status=gst_status)

        # Filter by state
        state = request.query_params.get('state', '').strip()
        if state:
            gst_records = gst_records.filter(state=state)

        serializer = GSTRegistrationListSerializer(gst_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = GSTRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "GSTIN added successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_detail(request, pk):

    try:
        gst_record = GSTRegistration.objects.get(pk=pk)
    except GSTRegistration.DoesNotExist:
        return Response(
            {"error": "GSTIN record not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = GSTRegistrationSerializer(gst_record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = GSTRegistrationSerializer(gst_record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "GSTIN updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = GSTRegistrationSerializer(gst_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "GSTIN partially updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        gst_record.delete()
        return Response(
            {"message": "GSTIN deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activate_gstin(request, pk):
    try:
        gst_record = GSTRegistration.objects.get(pk=pk)
    except GSTRegistration.DoesNotExist:
        return Response(
            {"error": "GSTIN record not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if gst_record.status == 'Active':
        return Response(
            {"error": "GSTIN is already active"},
            status=status.HTTP_400_BAD_REQUEST
        )

    gst_record.status = 'Active'
    gst_record.save()
    return Response(
        {"message": "GSTIN activated successfully", "data": GSTRegistrationSerializer(gst_record).data},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def deactivate_gstin(request, pk):
    try:
        gst_record = GSTRegistration.objects.get(pk=pk)
    except GSTRegistration.DoesNotExist:
        return Response(
            {"error": "GSTIN record not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if gst_record.status == 'Inactive':
        return Response(
            {"error": "GSTIN is already inactive"},
            status=status.HTTP_400_BAD_REQUEST
        )

    gst_record.status = 'Inactive'
    gst_record.save()
    return Response(
        {"message": "GSTIN deactivated successfully", "data": GSTRegistrationSerializer(gst_record).data},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gst_stats(request):
    return Response({
        "total_gstins": GSTRegistration.objects.count(),
        "active":       GSTRegistration.objects.filter(status='Active').count(),
        "pending":      GSTRegistration.objects.filter(status='Pending').count(),
        "inactive":     GSTRegistration.objects.filter(status='Inactive').count(),
    }, status=status.HTTP_200_OK)