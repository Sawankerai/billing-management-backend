from rest_framework import serializers
from .models import SalesReport
from decimal import Decimal


class SalesReportSerializer(serializers.ModelSerializer):
    net_sales    = serializers.ReadOnlyField()
    outstanding  = serializers.ReadOnlyField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model  = SalesReport
        fields = [
            'id', 'invoice_no', 'date', 'customer_name', 'company',
            'item', 'category', 'qty_sold', 'taxable', 'tax',
            'gross_sales', 'returns', 'net_sales', 'paid',
            'outstanding', 'due_date', 'status', 'status_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalesReportListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view"""
    net_sales   = serializers.ReadOnlyField()
    outstanding = serializers.ReadOnlyField()

    class Meta:
        model  = SalesReport
        fields = [
            'id', 'invoice_no', 'date', 'customer_name',
            'company', 'gross_sales', 'returns', 'net_sales',
            'paid', 'outstanding', 'status',
        ]