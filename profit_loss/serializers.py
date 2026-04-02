from rest_framework import serializers
from .models import ProfitLossStatement, LedgerPL, PLBreakdown


class ProfitLossStatementSerializer(serializers.ModelSerializer):
    gross_margin_percent = serializers.SerializerMethodField()

    class Meta:
        model = ProfitLossStatement
        fields = [
            'id',
            'period',
            'branch',
            'cost_center',
            'period_from',
            'period_to',
            'net_revenue',
            'cogs',
            'gross_profit',
            'operating_expenses',
            'net_profit',
            'gross_margin_percent',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'gross_profit',
            'net_profit',
            'gross_margin_percent',
            'created_at',
            'updated_at',
        ]

    def get_gross_margin_percent(self, obj):
        if obj.net_revenue == 0:
            return 0
        return round((obj.gross_profit / obj.net_revenue) * 100, 1)


class LedgerPLSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = LedgerPL
        fields = [
            'id',
            'category',
            'category_display',
            'account',
            'amount',
            'period_from',
            'period_to',
            'branch',
            'cost_center',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'category_display',
            'created_at',
            'updated_at',
        ]


class PLBreakdownSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = PLBreakdown
        fields = [
            'id',
            'category',
            'category_display',
            'amount',
            'notes',
            'period_from',
            'period_to',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'category_display',
            'created_at',
            'updated_at',
        ]