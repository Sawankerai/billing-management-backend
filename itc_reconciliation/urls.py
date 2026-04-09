from django.urls import path
from . import views

urlpatterns = [
    path('', views.itc_list, name='itc-list'),
    path('<int:pk>/', views.itc_detail, name='itc-detail'),
    path('<int:pk>/resolve/', views.resolve_mismatch, name='itc-resolve'),
    path('<int:pk>/match/', views.mark_matched, name='itc-match'),
    path('stats/', views.itc_stats, name='itc-stats'),
    path('summary/', views.itc_summary, name='itc-summary'),
]