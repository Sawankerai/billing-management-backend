from rest_framework import serializers
from .models import BarcodeDevice, StockMovement


class BarcodeDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeDevice
        fields = [
            'id',
            'name',
            'device_uid',
            'status',
            'last_scan_barcode',
            'last_scan_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id',
            'movement_number',
            'movement_type',
            'movement_type_display',
            'barcode',
            'sku',
            'product_name',
            'quantity',
            'from_location',
            'to_location',
            'reference',
            'status',
            'status_display',
            'device',
            'device_name',
            'scanned_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'movement_number',
            'movement_type_display',
            'status_display',
            'device_name',
            'created_at',
            'updated_at',
        ]


class BarcodeScanSerializer(serializers.Serializer):
    """
    Used for the Start Scan / Manual Entry action from the scanner panel.
    Auto-creates a StockMovement from a scan event.
    """
    device_id = serializers.IntegerField(required=False, allow_null=True)
    scan_mode = serializers.ChoiceField(choices=['stock_in', 'stock_out', 'transfer'])
    barcode = serializers.CharField(max_length=200)
    sku = serializers.CharField(max_length=100)
    product_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=1)
    from_location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    to_location = serializers.CharField(max_length=100)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)


class CreateTransferSerializer(serializers.Serializer):
    """
    Used for the Create Transfer button on the tracking panel.
    """
    sku = serializers.CharField(max_length=100)
    product_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=1)
    from_location = serializers.CharField(max_length=100)
    to_location = serializers.CharField(max_length=100)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    device_id = serializers.IntegerField(required=False, allow_null=True)