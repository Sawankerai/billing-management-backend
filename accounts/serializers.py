from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.account_name', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    balance_type_display = serializers.CharField(source='get_balance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Account
        fields = [
            'id',
            'account_code',
            'account_name',
            'account_type',
            'account_type_display',
            'parent',
            'parent_name',
            'opening_balance',
            'balance_type',
            'balance_type_display',
            'debit',
            'credit',
            'balance',
            'status',
            'status_display',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'parent_name',
            'account_type_display',
            'balance_type_display',
            'status_display',
            'created_at',
            'updated_at',
        ]