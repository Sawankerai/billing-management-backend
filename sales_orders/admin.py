from django.contrib import admin
from .models import SalesOrder, SalesOrderItem

admin.site.register(SalesOrder)
admin.site.register(SalesOrderItem)