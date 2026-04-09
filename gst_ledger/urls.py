from django.urls import path
from . import views

urlpatterns = [
    path('', views.gst_ledger_list, name='gst-ledger-list'),
    path('<int:pk>/', views.gst_ledger_detail, name='gst-ledger-detail'),
    path('input/', views.input_gst_ledger, name='gst-ledger-input'),
    path('output/', views.output_gst_ledger, name='gst-ledger-output'),
    path('summary/', views.gst_ledger_summary, name='gst-ledger-summary'),
    path('stats/', views.gst_ledger_stats, name='gst-ledger-stats'),
]