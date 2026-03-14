from rest_framework import serializers
from .models import StockAdjustment, StockAdjustmentItem
from core.models import Product


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Product
        fields = ['id', 'name', 'sku']


class StockAdjustmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model   = StockAdjustmentItem
        exclude = ['adjustment']


class StockAdjustmentSerializer(serializers.ModelSerializer):
    items      = StockAdjustmentItemSerializer(many=True)
    product    = ProductInfoSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model  = StockAdjustment
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        adjustment = StockAdjustment.objects.create(**validated_data)
        for item in items_data:
            StockAdjustmentItem.objects.create(adjustment=adjustment, **item)
        return adjustment

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                StockAdjustmentItem.objects.create(adjustment=instance, **item)
        return instance