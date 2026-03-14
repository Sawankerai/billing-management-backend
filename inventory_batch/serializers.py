from rest_framework import serializers
from .models import Batch, BatchItem


class BatchItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchItem
        exclude = ['batch']


class BatchSerializer(serializers.ModelSerializer):
    items = BatchItemSerializer(many=True)

    class Meta:
        model = Batch
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        batch = Batch.objects.create(**validated_data)
        for item in items_data:
            BatchItem.objects.create(batch=batch, **item)
        return batch

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                BatchItem.objects.create(batch=instance, **item)
        return instance
    
