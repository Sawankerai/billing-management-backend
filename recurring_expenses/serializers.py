from rest_framework import serializers
from .models import RecurringExpense
from django.utils import timezone

class RecurringExpenseSerializer(serializers.ModelSerializer):

    # Human-readable display labels
    category_display  = serializers.CharField(
        source='get_category_display',  read_only=True)
    frequency_display = serializers.CharField(
        source='get_frequency_display', read_only=True)
    status_display    = serializers.CharField(
        source='get_status_display',    read_only=True)

    # Computed — is next_run within 7 days?
    is_due_soon = serializers.SerializerMethodField()

    class Meta:
        model  = RecurringExpense
        fields = [
            'id',
            'template_name',       
            'category',            
            'category_display',    
            'frequency',          
            'frequency_display',  
            'next_run',            
            'amount',              
            'status',             
            'status_display',     
            'vendor_payee',
            'notes',
            'auto_post_ledger',
            'notify_before_run',
            'is_due_soon',         
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_due_soon(self, obj):
        from datetime import timedelta
        today = timezone.now().date()
        return today <= obj.next_run <= today + timedelta(days=7)