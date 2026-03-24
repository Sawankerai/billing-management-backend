from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.sales_order_stats, name='sales-order-stats'),
    path('', views.sales_order_list, name='sales-order-list'),
    path('<int:pk>/', views.sales_order_detail, name='sales-order-detail'),
    path('<int:pk>/items/', views.sales_order_item_list, name='sales-order-item-list'),
    path('<int:pk>/items/<int:item_pk>/', views.sales_order_item_detail, name='sales-order-item-detail'),
    path('<int:pk>/approve/', views.approve_order, name='sales-order-approve'),
    path('<int:pk>/reject/', views.reject_order, name='sales-order-reject'),
    path('<int:pk>/dispatch/', views.dispatch_order, name='sales-order-dispatch'),
]