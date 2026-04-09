from rest_framework import serializers
from .models import GSTLedger


class GSTLedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model  = GSTLedger
        fields = [
            'id',
            'ledger_type',
            'voucher_type',
            'ref',
            'date',
            'debit',
            'credit',
            'cgst',
            'sgst',
            'igst',
            'cess',
            'taxable_value',
            'gstin',
            'party_name',
            'narration',
            'is_posted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        ledger_type  = data.get('ledger_type')
        debit        = data.get('debit', 0)
        credit       = data.get('credit', 0)

        if ledger_type == 'Input' and debit <= 0:
            raise serializers.ValidationError(
                {"debit": "Input GST entries must have a positive debit amount."}
            )
        if ledger_type == 'Output' and credit <= 0:
            raise serializers.ValidationError(
                {"credit": "Output GST entries must have a positive credit amount."}
            )
        return data


class GSTLedgerListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = GSTLedger
        fields = [
            'id',
            'ledger_type',
            'voucher_type',
            'ref',
            'date',
            'debit',
            'credit',
            'party_name',
            'is_posted',
        ]