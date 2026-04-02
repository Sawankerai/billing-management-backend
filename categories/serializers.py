from rest_framework import serializers
from .models import ExpenseCategory

class ExpenseCategorySerializer(serializers.ModelSerializer):

    
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

  
    default_tax_display = serializers.SerializerMethodField()

    class Meta:
        model  = ExpenseCategory
        fields = [
            'id',
            'name',               
            'code',               
            'default_tax',        
            'default_tax_display',
            'status',             
            'status_display',     
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_default_tax_display(self, obj):
        return f"{int(obj.default_tax)}%"