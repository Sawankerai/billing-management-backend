from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    voucher_type_display = serializers.CharField(source='get_voucher_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    gst_tax_rate_display = serializers.CharField(source='get_gst_tax_rate_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'voucher_number',
            'voucher_type',
            'voucher_type_display',
            'transaction_date',
            'reference_no',
            'debit_account',
            'credit_account',
            'amount',
            'gst_tax_rate',
            'gst_tax_rate_display',
            'narration',
            'status',
            'status_display',
            'source',
            'source_display',
            'is_tax_entry',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'voucher_number',
            'voucher_type_display',
            'status_display',
            'source_display',
            'gst_tax_rate_display',
            'is_tax_entry',
            'created_at',
            'updated_at',
        ]


class SaveDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'voucher_type',
            'transaction_date',
            'reference_no',
            'debit_account',
            'credit_account',
            'amount',
            'gst_tax_rate',
            'narration',
            'source',
        ]