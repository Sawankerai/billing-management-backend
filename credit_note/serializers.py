from rest_framework import serializers
from .models import CreditNote
from core.models import Customer


class CustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Customer
        fields = ['id', 'name', 'gst_number']


class CreditNoteSerializer(serializers.ModelSerializer):
    customer    = CustomerInfoSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True
    )

    class Meta:
        model  = CreditNote
        fields = '__all__'

    def create(self, validated_data):
        return CreditNote.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance