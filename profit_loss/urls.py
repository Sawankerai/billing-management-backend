from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.pl_stats, name='pl-stats'),
    path('statements/', views.pl_statement_list, name='pl-statement-list'),
    path('statements/<int:pk>/', views.pl_statement_detail, name='pl-statement-detail'),
    path('ledger/', views.ledger_pl_list, name='ledger-pl-list'),
    path('ledger/<int:pk>/', views.ledger_pl_detail, name='ledger-pl-detail'),
    path('breakdown/', views.pl_breakdown_list, name='pl-breakdown-list'),
    path('breakdown/<int:pk>/', views.pl_breakdown_detail, name='pl-breakdown-detail'),
]