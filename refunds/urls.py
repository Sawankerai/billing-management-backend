from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.refund_stats, name='refund-stats'),
    path('', views.refund_list, name='refund-list'),
    path('<int:pk>/', views.refund_detail, name='refund-detail'),
    path('<int:pk>/process/', views.process_refund, name='refund-process'),
    path('<int:pk>/reject/', views.reject_refund, name='refund-reject'),
    path('<int:pk>/cancel/', views.cancel_refund, name='refund-cancel'),
]