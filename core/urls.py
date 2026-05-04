from django.urls import path
from . import views

urlpatterns = [
    # Customers
    path('customers/', views.customer_list),
    path('customers/stats/', views.customer_stats, name='customer-stats'),
    path('customers/<int:pk>/', views.customer_detail),
    path('customers/<int:pk>/full-details/', views.customer_full_details, name='customer-full-details'),
    # Related Customer Data
    path('customers/<int:pk>/invoices/', views.customer_invoices, name='customer-invoices'),
    path('customers/<int:pk>/payments/', views.customer_payments, name='customer-payments'),
    path('customers/<int:pk>/ledgers/', views.customer_ledgers, name='customer-ledgers'),

  

    # Vendors
    path('vendors/', views.vendor_list),
    path('vendors/<int:pk>/', views.vendor_detail),
    path('vendors/<int:pk>/stats/', views.vendor_stats, name='vendor-stats'),
    path('vendors/<int:pk>/full-details/', views.vendor_full_details, name='vendor-full-details'),
    
    # Related Vendor Data.
    path('vendors/<int:pk>/bills/', views.vendor_bills,name='vendor-bills'),
    path('vendors/<int:pk>/payments/', views.vendor_payments,name='vendor-payments'),
    path('vendors/<int:pk>/ledgers/',views.vendor_ledgers,name='vendor-ledgers'),


    
    # Products
    path('products/', views.product_list),
    path('products/stats/', views.product_stats, name='product-stats'),
    path('products/<int:pk>/', views.product_detail),
    path('products/<int:pk>/stats/', views.product_detail_stats, name='product-detail-stats'),
    path('products/<int:pk>/full-details/', views.product_full_details, name='product-full-details'),

    # Related Product Data.
    path('products/<int:pk>/sales/', views.product_sales, name='product-sales'),
    path('products/<int:pk>/purchases/', views.product_purchases, name='product-purchases'),
    path('products/<int:pk>/stock/', views.product_stock, name='product-stock'),
    path('products/<int:pk>/batches/', views.product_batches, name='product-batches'),
    path('products/<int:pk>/adjustments/', views.product_adjustments, name='product-adjustments'),
    path('products/<int:pk>/movements/', views.product_movements, name='product-movements'),
    path('products/<int:pk>/transactions/', views.product_transactions, name='product-transactions'),

    # Categories
    path('categories/', views.category_list),
    path('categories/<int:pk>/', views.category_detail),
    path('categories/stats/', views.category_stats, name='category-stats'),

    # Related product data.
    
]
