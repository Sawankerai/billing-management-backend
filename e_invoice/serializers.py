from rest_framework import serializers
from .models import EInvoice, IRNAuditLog
import re


class IRNAuditLogSerializer(serializers.ModelSerializer):

    class Meta:
        model  = IRNAuditLog
        fields = ['id', 'action', 'remarks', 'performed_at']
        read_only_fields = ['id', 'performed_at']


class EInvoiceSerializer(serializers.ModelSerializer):

    audit_logs = IRNAuditLogSerializer(many=True, read_only=True)

    class Meta:
        model  = EInvoice
        fields = [
            'id',
            'invoice_number',
            'customer_name',
            'customer_gstin',
            'invoice_date',
            'taxable_value',
            'gst_amount',
            'total_amount',
            'place_of_supply',
            'hsn_sac_code',
            'irn',
            'qr_code',
            'irn_status',
            'irn_generated_at',
            'cancellation_reason',
            'rejection_reason',
            'is_eligible',
            'notes',
            'audit_logs',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'irn', 'qr_code', 'irn_generated_at', 'created_at', 'updated_at']

    def validate_customer_gstin(self, value):
        if value:
            gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
            if not re.match(gstin_pattern, value.upper()):
                raise serializers.ValidationError("Invalid GSTIN format. Expected format: 29AABCU9603R1ZV")
            return value.upper()
        return value

    def validate(self, data):
        taxable_value = data.get('taxable_value', 0)
        gst_amount    = data.get('gst_amount', 0)
        total_amount  = data.get('total_amount', 0)
        if float(total_amount) != float(taxable_value) + float(gst_amount):
            raise serializers.ValidationError(
                "total_amount must equal taxable_value + gst_amount."
            )
        return data


class EInvoiceListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = EInvoice
        fields = [
            'id',
            'invoice_number',
            'customer_name',
            'invoice_date',
            'taxable_value',
            'gst_amount',
            'total_amount',
            'irn_status',
            'is_eligible',
        ]