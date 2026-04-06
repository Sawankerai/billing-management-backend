from rest_framework import serializers
from .models import EWayBill, EWayBillAuditLog

class EWayBillListSerializer(serializers.ModelSerializer):
    """Lightweight serializer used for list views."""

    class Meta:
        model  = EWayBill
        fields = [
            'id',
            'challan_number',
            'customer_name',
            'challan_date',
            'vehicle_number',
            'total_value',
            'ewaybill_status',
        ]

class EWayBillSerializer(serializers.ModelSerializer):
    """Full serializer used for create / retrieve / update."""

    class Meta:
        model  = EWayBill
        fields = '__all__'
        read_only_fields = [
            'ewaybill_number',
            'ewaybill_status',
            'valid_upto',
            'generated_at',
            'cancellation_reason',
            'created_at',
            'updated_at',
        ]

    def validate_vehicle_number(self, value):
        """Basic vehicle-number format check (e.g. KA01AB2034)."""
        import re
        pattern = r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$'
        if not re.match(pattern, value.upper().replace(' ', '')):
            raise serializers.ValidationError(
                "Invalid vehicle number format. Expected format: KA01AB2034"
            )
        return value.upper().replace(' ', '')

    def validate_total_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total value must be greater than zero.")
        return value

    def validate_distance_km(self, value):
        if value < 0:
            raise serializers.ValidationError("Distance cannot be negative.")
        return value

class EWayBillAuditLogSerializer(serializers.ModelSerializer):

    class Meta:
        model  = EWayBillAuditLog
        fields = ['id', 'action', 'remarks', 'performed_at']