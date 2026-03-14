from django.urls import path
from . import views

urlpatterns = [
    # Customers
    path('customers/', views.customer_list),
    path('customers/<int:pk>/', views.customer_detail),

    # Vendors
    path('vendors/', views.vendor_list),
    path('vendors/<int:pk>/', views.vendor_detail),
    
    # Products
    path('products/', views.product_list),
    path('products/<int:pk>/', views.product_detail),

    # Categories
    path('categories/', views.category_list),
    path('categories/<int:pk>/', views.category_detail),
    path('categories/stats/', views.category_stats, name='category-stats'),
]