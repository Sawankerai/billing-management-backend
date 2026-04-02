from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum

from .models import ProfitLossStatement, LedgerPL, PLBreakdown
from .serializers import (
    ProfitLossStatementSerializer,
    LedgerPLSerializer,
    PLBreakdownSerializer,
)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pl_stats(request):
    period_from = request.query_params.get('from', '').strip()
    period_to = request.query_params.get('to', '').strip()
    branch = request.query_params.get('branch', '').strip()
    cost_center = request.query_params.get('cost_center', '').strip()

    statements = ProfitLossStatement.objects.all()

    if period_from:
        statements = statements.filter(period_from__gte=period_from)
    if period_to:
        statements = statements.filter(period_to__lte=period_to)
    if branch and branch != 'All Branches':
        statements = statements.filter(branch=branch)
    if cost_center and cost_center != 'All Centers':
        statements = statements.filter(cost_center=cost_center)

    net_revenue = statements.aggregate(total=Sum('net_revenue'))['total'] or 0
    cogs = statements.aggregate(total=Sum('cogs'))['total'] or 0
    gross_profit = statements.aggregate(total=Sum('gross_profit'))['total'] or 0
    operating_expenses = statements.aggregate(total=Sum('operating_expenses'))['total'] or 0
    net_profit = statements.aggregate(total=Sum('net_profit'))['total'] or 0
    gross_margin = round((gross_profit / net_revenue) * 100, 1) if net_revenue else 0

    return Response({
        "revenue_net": net_revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "operating_expenses": operating_expenses,
        "net_profit": net_profit,
        "gross_margin_percent": gross_margin,
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pl_statement_list(request):
    if request.method == 'GET':
        period_from = request.query_params.get('from', '').strip()
        period_to = request.query_params.get('to', '').strip()
        branch = request.query_params.get('branch', '').strip()
        cost_center = request.query_params.get('cost_center', '').strip()

        statements = ProfitLossStatement.objects.all()

        if period_from:
            statements = statements.filter(period_from__gte=period_from)
        if period_to:
            statements = statements.filter(period_to__lte=period_to)
        if branch and branch != 'All Branches':
            statements = statements.filter(branch=branch)
        if cost_center and cost_center != 'All Centers':
            statements = statements.filter(cost_center=cost_center)

        serializer = ProfitLossStatementSerializer(statements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ProfitLossStatementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pl_statement_detail(request, pk):
    try:
        statement = ProfitLossStatement.objects.get(pk=pk)
    except ProfitLossStatement.DoesNotExist:
        return Response({"error": "P&L Statement not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfitLossStatementSerializer(statement)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfitLossStatementSerializer(statement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = ProfitLossStatementSerializer(statement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        statement.delete()
        return Response({"message": "P&L Statement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ledger_pl_list(request):
    if request.method == 'GET':
        period_from = request.query_params.get('from', '').strip()
        period_to = request.query_params.get('to', '').strip()
        branch = request.query_params.get('branch', '').strip()
        cost_center = request.query_params.get('cost_center', '').strip()
        category = request.query_params.get('category', '').strip()

        entries = LedgerPL.objects.all()

        if period_from:
            entries = entries.filter(period_from__gte=period_from)
        if period_to:
            entries = entries.filter(period_to__lte=period_to)
        if branch and branch != 'All Branches':
            entries = entries.filter(branch=branch)
        if cost_center and cost_center != 'All Centers':
            entries = entries.filter(cost_center=cost_center)
        if category:
            entries = entries.filter(category=category)

        serializer = LedgerPLSerializer(entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = LedgerPLSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ledger_pl_detail(request, pk):
    try:
        entry = LedgerPL.objects.get(pk=pk)
    except LedgerPL.DoesNotExist:
        return Response({"error": "Ledger P&L entry not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LedgerPLSerializer(entry)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LedgerPLSerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = LedgerPLSerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        entry.delete()
        return Response({"message": "Ledger P&L entry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pl_breakdown_list(request):
    if request.method == 'GET':
        period_from = request.query_params.get('from', '').strip()
        period_to = request.query_params.get('to', '').strip()

        breakdowns = PLBreakdown.objects.all()

        if period_from:
            breakdowns = breakdowns.filter(period_from__gte=period_from)
        if period_to:
            breakdowns = breakdowns.filter(period_to__lte=period_to)

        serializer = PLBreakdownSerializer(breakdowns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PLBreakdownSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pl_breakdown_detail(request, pk):
    try:
        breakdown = PLBreakdown.objects.get(pk=pk)
    except PLBreakdown.DoesNotExist:
        return Response({"error": "P&L Breakdown entry not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PLBreakdownSerializer(breakdown)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PLBreakdownSerializer(breakdown, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = PLBreakdownSerializer(breakdown, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        breakdown.delete()
        return Response({"message": "P&L Breakdown entry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)