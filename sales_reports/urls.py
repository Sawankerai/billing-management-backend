from django.urls import path
from . import views

urlpatterns = [
   
    path('', views.sales_report_list,name='sales-report-list'),
    path('<int:pk>/', views.sales_report_detail, name='sales-report-detail'),

    # Report sections
    path('summary/', views.sales_summary,name='sales-summary'),
    path('performance/', views.sales_performance, name='sales-performance'),
    path('top-customers/', views.top_customers, name='top-customers'),
    path('top-products/',  views.top_products, name='top-products'),
    path('aging/', views.aging_buckets,name='aging-buckets'),
    path('register/', views.sales_register,name='sales-register'),
    path('stats/', views.sales_report_stats, name='sales-stats'),
    path('full/', views.sales_full_report,  name='sales-full'),
]