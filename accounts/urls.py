from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.account_stats, name='account-stats'),
    path('', views.account_list, name='account-list'),
    path('<int:pk>/', views.account_detail, name='account-detail'),
    path('<int:pk>/activate/', views.activate_account, name='account-activate'),
    path('<int:pk>/deactivate/', views.deactivate_account, name='account-deactivate'),
]