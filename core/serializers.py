from rest_framework import serializers
from .models import Customer, Vendor, Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    is_low_stock    = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    category_name   = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model  = Product
        fields = '__all__'



from .models import VendorBill, VendorBillItem
from payments.models import Payment


class VendorBillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBillItem
        fields = [
            'item_name', 'description',
            'quantity', 'unit', 'rate',
            'discount', 'tax_rate', 'total',
        ]



class VendorBillSerializer(serializers.ModelSerializer):
    items       = VendorBillItemSerializer(many=True, required=False)
    outstanding = serializers.SerializerMethodField()
    bill_number = serializers.SerializerMethodField()

    class Meta:
        model = VendorBill
        fields = [
            # Identity
            'id', 'bill_number',
            'bill_type',        # GST / Non-GST
            'date', 'due_date', 'status',
            # Financials
            'sub_total', 'discount', 'total_tax',
            'cgst', 'sgst', 'igst',
            'total_amount', 'paid_amount', 'outstanding',
            # Notes
            'notes', 'terms_conditions', 'created_at',
            # Line items
            'items',
        ]

    def get_outstanding(self, obj):
        return str(obj.total_amount - obj.paid_amount)

    def get_bill_number(self, obj):
        return f"BILL-{obj.id:03d}"

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = VendorBill.objects.create(**validated_data)
        for item_data in items_data:
            VendorBillItem.objects.create(bill=bill, **item_data)
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                VendorBillItem.objects.create(bill=instance, **item_data)
        return instance


# â”€â”€ Vendor Payment (same Payment model as customer â€” filtered by vendor in view) â”€â”€
class VendorPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            # Identity
            'id', 'receipt_number', 'date',
            # Details
            'payment_mode', 'amount', 'advance_amount',
            # Status
            'status', 'gateway_status', 'allocation_status',
            # Allocation
            'invoice_allocation', 'notes',
            # Timestamps
            'created_at', 'updated_at',
        ]


# â”€â”€ Vendor Ledger Entry (mirrors LedgerEntrySerializer) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class VendorLedgerEntrySerializer(serializers.Serializer):
    date = serializers.DateField(allow_null=True)
    entry_type = serializers.CharField()
    ref_no = serializers.CharField()
    product = serializers.CharField(allow_blank=True)
    qty = serializers.CharField(allow_blank=True)
    debit = serializers.DecimalField(max_digits=12, decimal_places=2)
    credit = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
