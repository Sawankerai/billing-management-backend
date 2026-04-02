from django.urls import path
from . import views

urlpatterns = [
    # Customer Ledger
    path('customers/',views.customer_list,name='ledger-customers'),
    path('entries/',views.ledger_entries,name='ledger-entries'),
    path('stats/',views.ledger_stats,name='ledger-stats'),

    # Supplier Ledger
    path('vendors/',views.vendor_list,name='supplier-vendors'),
    path('supplier/entries/',views.supplier_ledger_entries,name='supplier-entries'),
    path('supplier/stats/',views.supplier_ledger_stats,name='supplier-stats'),
]