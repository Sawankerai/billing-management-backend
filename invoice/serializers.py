from dataclasses import fields

from rest_framework import serializers
from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            #  'id',        
            'item_name',
            'description',
            'quantity',
            'unit',
            'rate',
            'discount',
            'tax_rate',
            'total',
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'invoice_id',
            'items',
            'invoice_type',
            'invoice_date',
            'due_date',
            'sub_total',
            'total_tax',
            'cgst',
            'sgst',
            'igst',
            'discount',
            'total_amount',
            'paid_amount',
            'total_due',
            'notes',
            'terms_conditions',
            'digital_signature',
            'status',
            'created_at',
            'customer',
        ] 

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)

        for item in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item)

        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                InvoiceItem.objects.create(invoice=instance, **item)

        return instance