from django.urls import path
from . import views

urlpatterns = [
    path('', views.gst_list, name='gst-list'),
    path('<int:pk>/', views.gst_detail, name='gst-detail'),

    path('<int:pk>/activate/', views.activate_gstin, name='gst-activate'),

    path('<int:pk>/deactivate/', views.deactivate_gstin, name='gst-deactivate'),

    path('stats/', views.gst_stats, name='gst-stats'),
]