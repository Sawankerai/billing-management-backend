from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RecurringExpense
from .serializers import RecurringExpenseSerializer


@api_view(['GET', 'POST'])
def recurring_expense_list(request):

    if request.method == 'GET':
        recurring = RecurringExpense.objects.all()
        serializer = RecurringExpenseSerializer(recurring, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RecurringExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def recurring_expense_detail(request, pk):

    try:
        recurring = RecurringExpense.objects.get(pk=pk)
    except RecurringExpense.DoesNotExist:
        return Response(
            {"error": "Recurring Expense not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = RecurringExpenseSerializer(recurring)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RecurringExpenseSerializer(recurring, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = RecurringExpenseSerializer(
            recurring, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        recurring.delete()
        return Response(
            {"message": "Recurring Expense deleted"},
            status=status.HTTP_204_NO_CONTENT
        )