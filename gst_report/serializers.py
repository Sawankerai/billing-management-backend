from rest_framework import serializers
from .models import GSTTransaction


class GSTTransactionListSerializer(serializers.ModelSerializer):

    total_tax = serializers.SerializerMethodField()

    class Meta:
        model  = GSTTransaction
        fields = [
            'id',
            'transaction_type',
            'transaction_date',
            'invoice_number',
            'party_name',
            'taxable_amount',
            'total_tax',
            'invoice_status',
        ]

    def get_total_tax(self, obj):
        return obj.cgst_amount + obj.sgst_amount + obj.igst_amount


class GSTTransactionSerializer(serializers.ModelSerializer):

    total_tax = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = GSTTransaction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_total_tax(self, obj):
        return obj.cgst_amount + obj.sgst_amount + obj.igst_amount

    def validate(self, data):
        cgst = data.get('cgst_amount', 0)
        sgst = data.get('sgst_amount', 0)
        igst = data.get('igst_amount', 0)

        if igst > 0 and (cgst > 0 or sgst > 0):
            raise serializers.ValidationError(
                "IGST and CGST/SGST cannot both be non-zero on the same transaction."
            )

        if cgst != sgst:
            raise serializers.ValidationError("CGST and SGST must be equal.")

        taxable = data.get('taxable_amount', 0)
        if taxable < 0:
            raise serializers.ValidationError("Taxable amount cannot be negative.")

        return data