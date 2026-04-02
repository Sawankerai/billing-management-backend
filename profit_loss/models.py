from django.db import models


class ProfitLossStatement(models.Model):
    period = models.CharField(max_length=50)
    branch = models.CharField(max_length=100, default='All Branches')
    cost_center = models.CharField(max_length=100, default='All Centers')
    period_from = models.DateField(blank=True, null=True)
    period_to = models.DateField(blank=True, null=True)
    net_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cogs = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    operating_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.gross_profit = self.net_revenue - self.cogs
        self.net_profit = self.gross_profit - self.operating_expenses
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.period} — Net Profit: {self.net_profit}"

    class Meta:
        db_table = 'profit_loss_statements'
        ordering = ['-period_from']


class LedgerPL(models.Model):
    CATEGORY_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
        ('Net Profit', 'Net Profit'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    account = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    period_from = models.DateField(blank=True, null=True)
    period_to = models.DateField(blank=True, null=True)
    branch = models.CharField(max_length=100, default='All Branches')
    cost_center = models.CharField(max_length=100, default='All Centers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} — {self.account} — {self.amount}"

    class Meta:
        db_table = 'ledger_pl'
        ordering = ['category', 'account']


class PLBreakdown(models.Model):
    CATEGORY_CHOICES = [
        ('Revenue (Gross)', 'Revenue (Gross)'),
        ('Returns/Discounts', 'Returns/Discounts'),
        ('Revenue (Net)', 'Revenue (Net)'),
        ('COGS', 'COGS'),
        ('Gross Profit', 'Gross Profit'),
        ('Operating Expenses', 'Operating Expenses'),
        ('Net Profit', 'Net Profit'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    period_from = models.DateField(blank=True, null=True)
    period_to = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} — {self.amount}"

    class Meta:
        db_table = 'pl_breakdown'
        ordering = ['id']