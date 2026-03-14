from django.urls import path
from . import views

urlpatterns = [
    path('adjustments/', views.adjustment_list, name='adjustment-list'),
    path('adjustments/<int:pk>/', views.adjustment_detail, name='adjustment-detail'),
    path('adjustments/save-draft/', views.adjustment_save_draft, name='adjustment-save-draft'),
    path('adjustments/stats/', views.adjustment_stats, name='adjustment-stats'),
]