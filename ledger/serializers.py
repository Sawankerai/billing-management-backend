from rest_framework import serializers
from .models import Invoice, Receipt, PurchaseInvoice, SupplierPayment
from core.models import Customer, Vendor


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Customer
        fields = ['id', 'name']


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Vendor
        fields = ['id', 'name']


class LedgerEntrySerializer(serializers.Serializer):
    date    = serializers.DateField(allow_null=True)
    voucher = serializers.CharField()
    ref     = serializers.CharField()
    debit   = serializers.DecimalField(max_digits=12, decimal_places=2)
    credit  = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)