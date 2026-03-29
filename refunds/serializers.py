from rest_framework import serializers
from .models import Refund


class RefundSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    refund_mode_display = serializers.CharField(source='get_refund_mode_display', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id',
            'refund_number',
            'customer_name',
            'refund_date',
            'refund_mode',
            'refund_mode_display',
            'amount',
            'currency',
            'status',
            'status_display',
            'reference',
            'credit_note',
            'reason',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'refund_number',
            'status_display',
            'refund_mode_display',
            'created_at',
            'updated_at',
        ]