from django.urls import path

from . import views


urlpatterns = [
    path("purchase-orders/", views.purchase_order_list, name="purchase-order-list"),
    path("purchase-orders/<int:pk>/",  views.purchase_order_detail, name="purchase-order-detail",  ),
    path("reports/purchase/", views.purchase_report, name="purchase-report"),
    path("reports/purchase/stats/", views.purchase_report_stats,  name="purchase-report-stats", ),
        
]