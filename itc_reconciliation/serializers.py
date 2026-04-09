from rest_framework import serializers
from .models import ITCReconciliation
import re


class ITCReconciliationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ITCReconciliation
        fields = [
            'id',
            'expense_ref',
            'vendor_name',
            'vendor_gstin',
            'date',
            'tax_amount',
            'cgst',
            'sgst',
            'igst',
            'cess',
            'taxable_value',
            'match_status',
            'mismatch_reason',
            'eligible',
            'eligible_amount',
            'invoice_document',
            'resolution_notes',
            'resolved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'resolved_at', 'created_at', 'updated_at']

    def validate_vendor_gstin(self, value):
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, value.upper()):
            raise serializers.ValidationError("Invalid Vendor GSTIN format.")
        return value.upper()

    def validate(self, data):
        match_status     = data.get('match_status')
        mismatch_reason  = data.get('mismatch_reason')
        eligible         = data.get('eligible')
        eligible_amount  = data.get('eligible_amount')

        if match_status == 'Mismatch' and not mismatch_reason:
            raise serializers.ValidationError(
                {"mismatch_reason": "Mismatch reason is required when match status is Mismatch."}
            )
        if match_status == 'Resolved':
            if not eligible:
                raise serializers.ValidationError(
                    {"eligible": "Eligible field is required when resolving a mismatch."}
                )
            if eligible_amount is None:
                raise serializers.ValidationError(
                    {"eligible_amount": "Eligible amount is required when resolving a mismatch."}
                )
        return data


class ITCReconciliationListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ITCReconciliation
        fields = [
            'id',
            'expense_ref',
            'vendor_name',
            'vendor_gstin',
            'date',
            'tax_amount',
            'match_status',
        ]


class ResolveMismatchSerializer(serializers.Serializer):
    mismatch_reason  = serializers.ChoiceField(choices=ITCReconciliation.MISMATCH_REASON_CHOICES)
    eligible         = serializers.ChoiceField(choices=ITCReconciliation.ELIGIBLE_CHOICES)
    eligible_amount  = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_document = serializers.FileField(required=False, allow_null=True)
    resolution_notes = serializers.CharField(required=False, allow_blank=True)