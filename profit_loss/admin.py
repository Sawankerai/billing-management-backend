from django.contrib import admin
from .models import ProfitLossStatement, LedgerPL, PLBreakdown

admin.site.register(ProfitLossStatement)
admin.site.register(LedgerPL)
admin.site.register(PLBreakdown)