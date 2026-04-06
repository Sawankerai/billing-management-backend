from rest_framework import serializers
from django.utils import timezone
from .models import GSTReturn, GSTReturnAuditLog


class GSTReturnListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = GSTReturn
        fields = [
            'id',
            'return_type',
            'period',
            'due_date',
            'status',
            'next_step',
        ]


class GSTReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model  = GSTReturn
        fields = '__all__'
        read_only_fields = [
            'status',
            'created_at',
            'updated_at',
        ]

    def validate(self, data):
        filing_date = data.get('filing_date')
        due_date    = data.get('due_date')
        if filing_date and due_date and filing_date < due_date:
            pass
        return data

    def validate_due_date(self, value):
        if not value:
            raise serializers.ValidationError("Due date is required.")
        return value


class GSTReturnUpdateStatusSerializer(serializers.Serializer):
    return_type  = serializers.ChoiceField(choices=GSTReturn.RETURN_TYPE_CHOICES)
    period       = serializers.CharField(max_length=20)
    status       = serializers.ChoiceField(choices=GSTReturn.STATUS_CHOICES)
    filing_date  = serializers.DateField(required=False, allow_null=True)
    arn_ack_no   = serializers.CharField(max_length=100, required=False, allow_blank=True)
    ack_file     = serializers.FileField(required=False, allow_null=True)
    notes        = serializers.CharField(required=False, allow_blank=True)
    late_fee     = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)
    interest     = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)

    def validate(self, data):
        if data.get('status') == 'Filed':
            if not data.get('filing_date'):
                raise serializers.ValidationError({"filing_date": "Filing date is required when status is Filed."})
            if not data.get('arn_ack_no'):
                raise serializers.ValidationError({"arn_ack_no": "ARN / ACK No is required when status is Filed."})
        return data


class GSTReturnAuditLogSerializer(serializers.ModelSerializer):

    class Meta:
        model  = GSTReturnAuditLog
        fields = ['id', 'action', 'remarks', 'performed_at']