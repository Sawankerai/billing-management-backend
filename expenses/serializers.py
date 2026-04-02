from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):

    
    cgst_amount  = serializers.ReadOnlyField()
    sgst_amount  = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()

    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    paid_via_display = serializers.CharField(source='get_paid_via_display', read_only=True)
    status_display   = serializers.CharField(source='get_status_display',   read_only=True)

    class Meta:
        model  = Expense
        fields = [
            'id',
            'expense_no',       
            'category',         
            'category_display', 
            'date',
            'vendor_payee',
            'amount',
            'cgst_rate',
            'sgst_rate',
            'cgst_amount',      
            'sgst_amount',      
            'total_amount',     
            'paid_via',
            'paid_via_display',
            'status',
            'status_display',
            'notes',
            'reference',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'expense_no', 'created_at', 'updated_at']