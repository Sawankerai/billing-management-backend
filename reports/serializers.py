from rest_framework import serializers


class SummarySerializer(serializers.Serializer):
    """Top summary cards"""
    total_expense  = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_expense    = serializers.DecimalField(max_digits=12, decimal_places=2)
    tax_paid       = serializers.DecimalField(max_digits=12, decimal_places=2)
    approved_count = serializers.IntegerField()
    pending_count  = serializers.IntegerField()
    rejected_count = serializers.IntegerField()


class ExpensePerformanceSerializer(serializers.Serializer):
    """Monthly performance table row"""
    period         = serializers.CharField()        # Feb 2026
    expenses       = serializers.IntegerField()     # count
    taxable        = serializers.DecimalField(max_digits=12, decimal_places=2)
    tax            = serializers.DecimalField(max_digits=12, decimal_places=2)
    total          = serializers.DecimalField(max_digits=12, decimal_places=2)
    approved       = serializers.IntegerField()
    pending        = serializers.IntegerField()


class TopCategorySerializer(serializers.Serializer):
    """Top categories table row"""
    category       = serializers.CharField()
    expenses       = serializers.IntegerField()
    tax            = serializers.DecimalField(max_digits=12, decimal_places=2)
    total          = serializers.DecimalField(max_digits=12, decimal_places=2)


class TopVendorSerializer(serializers.Serializer):
    """Top vendors table row"""
    vendor_payee   = serializers.CharField()
    expenses       = serializers.IntegerField()
    tax            = serializers.DecimalField(max_digits=12, decimal_places=2)
    total          = serializers.DecimalField(max_digits=12, decimal_places=2)


class ExpenseBreakdownSerializer(serializers.Serializer):
    """Expense breakdown table row"""
    date           = serializers.DateField()
    category       = serializers.CharField()
    vendor_payee   = serializers.CharField()
    taxable        = serializers.DecimalField(max_digits=12, decimal_places=2)
    tax            = serializers.DecimalField(max_digits=12, decimal_places=2)
    total          = serializers.DecimalField(max_digits=12, decimal_places=2)
    status         = serializers.CharField()