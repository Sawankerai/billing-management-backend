from django.urls import path
from . import views

urlpatterns = [
    path('gst-report/transactions/',views.gst_transaction_list,name='gst-transaction-list'),
    path('gst-report/transactions/<int:pk>/',views.gst_transaction_detail, name='gst-transaction-detail'),
    path('gst-report/summary/',views.gst_summary,name='gst-summary'),
    path('gst-report/monthly-position/',views.monthly_gst_position,name='gst-monthly-position'),
    path('gst-report/slab-breakup/', views.gst_slab_breakup,name='gst-slab-breakup'),
    path('gst-report/gstr3b-mapping/',views.gstr3b_mapping,name='gst-gstr3b-mapping'),
]