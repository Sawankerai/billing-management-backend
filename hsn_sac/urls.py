from django.urls import path
from . import views

urlpatterns = [
    path('', views.hsnsac_list, name='hsnsac-list'),
    path('<int:pk>/', views.hsnsac_detail, name='hsnsac-detail'),
    path('<int:pk>/activate/', views.activate_hsnsac, name='hsnsac-activate'),
    path('<int:pk>/deactivate/', views.deactivate_hsnsac, name='hsnsac-deactivate'),
    path('draft/', views.save_draft_hsnsac, name='hsnsac-draft'),
    path('stats/', views.hsnsac_stats, name='hsnsac-stats'),
]