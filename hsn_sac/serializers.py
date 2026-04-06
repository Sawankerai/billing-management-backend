from rest_framework import serializers
from .models import HsnSac


class HsnSacSerializer(serializers.ModelSerializer):

    class Meta:
        model  = HsnSac
        fields = [
            'id',
            'code',
            'type',
            'gst_rate',
            'status',
            'description',
            'effective_date',
            'map_to',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_gst_rate(self, value):
        valid_rates = [0, 0.1, 0.25, 1, 1.5, 3, 5, 6, 7.5, 12, 18, 28]
        if float(value) not in valid_rates:
            raise serializers.ValidationError(
                f"Invalid GST rate. Allowed rates: {valid_rates}"
            )
        return value

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("HSN/SAC code must contain digits only.")
        if len(value) not in [4, 6, 8]:
            raise serializers.ValidationError("HSN code must be 4, 6, or 8 digits. SAC code must be 4 or 6 digits.")
        return value


class HsnSacListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = HsnSac
        fields = [
            'id',
            'code',
            'description',
            'type',
            'gst_rate',
            'status',
            'map_to',
        ]