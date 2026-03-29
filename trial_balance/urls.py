from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.trial_balance_stats, name='trial-balance-stats'),
    path('', views.trial_balance_list, name='trial-balance-list'),
    path('entries/', views.trial_balance_entry_list, name='trial-balance-entry-list'),
    path('entries/<int:pk>/', views.trial_balance_entry_detail, name='trial-balance-entry-detail'),
    path('opening/accounts/', views.opening_balance_account_list, name='opening-balance-account-list'),
    path('opening/accounts/<int:pk>/', views.opening_balance_account_detail, name='opening-balance-account-detail'),
    path('opening/customers/', views.opening_balance_customer_list, name='opening-balance-customer-list'),
    path('opening/customers/<int:pk>/', views.opening_balance_customer_detail, name='opening-balance-customer-detail'),
]