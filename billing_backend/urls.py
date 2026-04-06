from django.contrib import admin
from django.urls import path, include
from core.views import CustomLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

     # Authentication endpoints
     path('api/login/', CustomLoginView.as_view(), name='login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh'),

     # App endpoints
    path('api/', include('core.urls')),
    path('api/', include('invoice.urls')),
   path('api/batch/', include('inventory_batch.urls')),
   path('api/stock/', include('stock_adjustment.urls')),
   path('api/inventory/', include('inventory_barcode.urls')),
   path('api/sales/', include('sales_orders.urls')),
   path('api/credit-notes/', include('credit_note.urls')),
   path('api/accounts/', include('accounts.urls')),
   path('api/transactions/', include('transactions.urls')),
   path('api/payments/', include('payments.urls')),
   path('api/refunds/', include('refunds.urls')),
   path('api/trial-balance/', include('trial_balance.urls')),
   path('api/reports/pl/', include('profit_loss.urls')),
   path('api/ledger/', include('ledger.urls')),
   path('api/', include('expenses.urls')),
   path('api/', include('categories.urls')),
   path('api/', include('recurring_expenses.urls')),
   path('api/reports/', include('reports.urls')),
   path('api/gst/', include('gst.urls')),
   path('api/hsn-sac/', include('hsn_sac.urls')),
   path('api/gst/compliance/e-invoice/', include('e_invoice.urls')),
   path('api/', include('ewaybill.urls')),
   path('api/', include('returns_calendar.urls')),
  

] 
