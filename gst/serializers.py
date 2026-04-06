from rest_framework import serializers
from .models import GSTRegistration
import re


class GSTRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = GSTRegistration
        fields = [
            'id',
            'gstin',
            'legal_name',
            'trade_name',
            'state',
            'registration_type',
            'effective_date',
            'return_frequency',
            'default_gst_rate',
            'rounding_rule',
            'place_of_supply_rule',
            'notes',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_gstin(self, value):
        """
        Validates the GSTIN format:
        2-digit state code + 10-char PAN + 1 entity number + Z + 1 check digit
        Example: 29AABCU9603R1ZV
        """
        gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gstin_pattern, value.upper()):
            raise serializers.ValidationError(
                "Invalid GSTIN format. Expected format: 29AABCU9603R1ZV"
            )
        return value.upper()

    def validate_default_gst_rate(self, value):
        valid_rates = [0, 0.1, 0.25, 1, 1.5, 3, 5, 6, 7.5, 12, 18, 28]
        if float(value) not in valid_rates:
            raise serializers.ValidationError(
                f"Invalid GST rate. Allowed rates: {valid_rates}"
            )
        return value


class GSTRegistrationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer used for the list/table view."""

    class Meta:
        model  = GSTRegistration
        fields = [
            'id',
            'gstin',
            'legal_name',
            'state',
            'registration_type',
            'status',
            'effective_date',
        ]