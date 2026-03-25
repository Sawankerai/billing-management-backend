from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.transaction_stats, name='transaction-stats'),
    path('', views.transaction_list, name='transaction-list'),
    path('draft/', views.save_draft, name='transaction-draft'),
    path('<int:pk>/', views.transaction_detail, name='transaction-detail'),
    path('<int:pk>/post/', views.post_voucher, name='transaction-post'),
    path('<int:pk>/cancel/', views.cancel_transaction, name='transaction-cancel'),
]