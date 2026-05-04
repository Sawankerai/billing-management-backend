from rest_framework import serializers

from .models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "item_name",
            "category",
            "description",
            "qty_ordered",
            "qty_returned",
            "taxable_value",
            "tax_amount",
            "gross_purchases",
            "returns_adjustments",
            "net_purchases",
        ]
        read_only_fields = ["id"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, required=False)
    taxable_value = serializers.SerializerMethodField()
    input_tax = serializers.SerializerMethodField()
    gross_purchases = serializers.SerializerMethodField()
    returns_adjustments = serializers.SerializerMethodField()
    net_purchases = serializers.SerializerMethodField()
    pending_value = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "bill_number",
            "order_date",
            "expected_receipt_date",
            "vendor_name",
            "vendor_company",
            "po_status",
            "debit_note_status",
            "received_value",
            "notes",
            "taxable_value",
            "input_tax",
            "gross_purchases",
            "returns_adjustments",
            "net_purchases",
            "pending_value",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "taxable_value",
            "input_tax",
            "gross_purchases",
            "returns_adjustments",
            "net_purchases",
            "pending_value",
            "created_at",
            "updated_at",
        ]

    def get_taxable_value(self, obj):
        return str(obj.taxable_value)

    def get_input_tax(self, obj):
        return str(obj.input_tax)

    def get_gross_purchases(self, obj):
        return str(obj.gross_purchases)

    def get_returns_adjustments(self, obj):
        return str(obj.returns_adjustments)

    def get_net_purchases(self, obj):
        return str(obj.net_purchases)

    def get_pending_value(self, obj):
        return str(obj.pending_value)

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseOrderItem.objects.create(order=instance, **item_data)

        return instance