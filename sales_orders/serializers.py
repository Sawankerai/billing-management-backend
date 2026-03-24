from rest_framework import serializers
from .models import SalesOrder, SalesOrderItem


class SalesOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = [
            'id',
            'product_name',
            'sku',
            'quantity',
            'dispatched_quantity',
            'rate',
            'tax',
            'total_price',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True, read_only=True)
    dispatch_status_display = serializers.CharField(source='get_dispatch_status_display', read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    dispatch_percentage = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrder
        fields = [
            'id',
            'so_number',
            'customer_name',
            'company_name',
            'order_date',
            'expected_dispatch_date',
            'shipping_address',
            'salesperson',
            'payment_terms',
            'order_value',
            'total_items',
            'dispatched_items',
            'dispatch_percentage',
            'dispatch_status',
            'dispatch_status_display',
            'approval_status',
            'approval_status_display',
            'notes',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'so_number',
            'dispatch_status_display',
            'approval_status_display',
            'dispatch_percentage',
            'created_at',
            'updated_at',
        ]

    def get_dispatch_percentage(self, obj):
        if obj.total_items == 0:
            return 0
        return round((obj.dispatched_items / obj.total_items) * 100)


class SalesOrderCreateSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True, required=False)

    class Meta:
        model = SalesOrder
        fields = [
            'customer_name',
            'company_name',
            'order_date',
            'expected_dispatch_date',
            'shipping_address',
            'salesperson',
            'payment_terms',
            'order_value',
            'total_items',
            'dispatched_items',
            'dispatch_status',
            'approval_status',
            'notes',
            'items',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        sales_order = SalesOrder.objects.create(**validated_data)
        for item_data in items_data:
            SalesOrderItem.objects.create(sales_order=sales_order, **item_data)
        sales_order.total_items = sales_order.items.count()
        sales_order.save()
        return sales_order

    def update(self, instance, validated_data):
        validated_data.pop('items', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ApproveOrderSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class DispatchOrderSerializer(serializers.Serializer):
    dispatched_items = serializers.IntegerField(min_value=0)
    notes = serializers.CharField(required=False, allow_blank=True)