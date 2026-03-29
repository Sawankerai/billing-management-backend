from rest_framework import serializers
from .models import OpeningBalanceAccount, OpeningBalanceCustomer, TrialBalanceEntry


class OpeningBalanceAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningBalanceAccount
        fields = [
            'id',
            'account_name',
            'debit',
            'credit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OpeningBalanceCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningBalanceCustomer
        fields = [
            'id',
            'customer_name',
            'debit',
            'credit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrialBalanceEntrySerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)

    class Meta:
        model = TrialBalanceEntry
        fields = [
            'id',
            'account_name',
            'account_type',
            'account_type_display',
            'debit',
            'credit',
            'balance',
            'period_from',
            'period_to',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'balance',
            'account_type_display',
            'created_at',
            'updated_at',
        ]