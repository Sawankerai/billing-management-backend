from rest_framework import serializers
from .models import Payment
from core.models import Customer


class CustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Customer
        fields = ['id', 'name']


class PaymentSerializer(serializers.ModelSerializer):
    customer    = CustomerInfoSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True
    )

    class Meta:
        model  = Payment
        fields = '__all__'

    def create(self, validated_data):
        return Payment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance