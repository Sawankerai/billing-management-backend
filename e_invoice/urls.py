from django.urls import path
from . import views

urlpatterns = [
    path('', views.einvoice_list, name='einvoice-list'),
    path('<int:pk>/', views.einvoice_detail, name='einvoice-detail'),
    path('<int:pk>/generate-irn/', views.generate_irn, name='einvoice-generate-irn'),
    path('<int:pk>/cancel-irn/', views.cancel_irn, name='einvoice-cancel-irn'),
    path('<int:pk>/audit-log/', views.irn_audit_log, name='einvoice-audit-log'),
    path('stats/', views.einvoice_stats, name='einvoice-stats'),
]