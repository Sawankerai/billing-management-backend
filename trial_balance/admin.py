from django.contrib import admin
from .models import OpeningBalanceAccount, OpeningBalanceCustomer, TrialBalanceEntry

admin.site.register(OpeningBalanceAccount)
admin.site.register(OpeningBalanceCustomer)
admin.site.register(TrialBalanceEntry)