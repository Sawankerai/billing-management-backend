from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CreditNote
from .serializers import CreditNoteSerializer


# --- List & Create ---
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def credit_note_list(request):
    if request.method == 'GET':
        credit_notes = CreditNote.objects.all().order_by('-created_at')
        serializer   = CreditNoteSerializer(credit_notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CreditNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Detail, Update, Delete ---
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def credit_note_detail(request, pk):
    try:
        credit_note = CreditNote.objects.get(pk=pk)
    except CreditNote.DoesNotExist:
        return Response({"error": "Credit Note not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CreditNoteSerializer(credit_note)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CreditNoteSerializer(credit_note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = CreditNoteSerializer(credit_note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        credit_note.delete()
        return Response({"message": "Credit Note deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# --- Approve ---
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def approve_credit_note(request, pk):
    try:
        credit_note = CreditNote.objects.get(pk=pk)
    except CreditNote.DoesNotExist:
        return Response({"error": "Credit Note not found"}, status=status.HTTP_404_NOT_FOUND)

    if credit_note.status == 'Approved':
        return Response({"error": "Credit Note is already approved"}, status=status.HTTP_400_BAD_REQUEST)

    credit_note.status = 'Approved'
    credit_note.save()
    return Response({
        "message": "Credit Note approved successfully",
        "data": CreditNoteSerializer(credit_note).data
    }, status=status.HTTP_200_OK)


# --- Issue ---
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def issue_credit_note(request, pk):
    try:
        credit_note = CreditNote.objects.get(pk=pk)
    except CreditNote.DoesNotExist:
        return Response({"error": "Credit Note not found"}, status=status.HTTP_404_NOT_FOUND)

    if credit_note.status == 'Issued':
        return Response({"error": "Credit Note is already issued"}, status=status.HTTP_400_BAD_REQUEST)

    credit_note.status = 'Issued'
    credit_note.save()
    return Response({
        "message": "Credit Note issued successfully",
        "data": CreditNoteSerializer(credit_note).data
    }, status=status.HTTP_200_OK)


# --- Cancel ---
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def cancel_credit_note(request, pk):
    try:
        credit_note = CreditNote.objects.get(pk=pk)
    except CreditNote.DoesNotExist:
        return Response({"error": "Credit Note not found"}, status=status.HTTP_404_NOT_FOUND)

    if credit_note.status == 'Cancelled':
        return Response({"error": "Credit Note is already cancelled"}, status=status.HTTP_400_BAD_REQUEST)

    credit_note.status = 'Cancelled'
    credit_note.save()
    return Response({
        "message": "Credit Note cancelled successfully",
        "data": CreditNoteSerializer(credit_note).data
    }, status=status.HTTP_200_OK)


# --- Stats for Dashboard Cards ---
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def credit_note_stats(request):
    return Response({
        "total_notes": CreditNote.objects.count(),
        "approved":    CreditNote.objects.filter(status='Approved').count(),
        "issued":      CreditNote.objects.filter(status='Issued').count(),
        "draft":       CreditNote.objects.filter(status='Draft').count(),
        "cancelled":   CreditNote.objects.filter(status='Cancelled').count(),
    }, status=status.HTTP_200_OK)