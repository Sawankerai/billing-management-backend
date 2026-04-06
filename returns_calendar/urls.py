from django.urls import path
from . import views

urlpatterns = [
    path('gst-returns/stats/',views.gstreturn_stats,name='gstreturn-stats'),
    path('gst-returns/',views.gstreturn_list,name='gstreturn-list'),
    path('gst-returns/<int:pk>/',views.gstreturn_detail,name='gstreturn-detail'),
    path('gst-returns/update-status/', views.update_gstreturn_status, name='gstreturn-update-status'),
    path('gst-returns/mark-overdue/',  views.mark_overdue,name='gstreturn-mark-overdue'),
    path('gst-returns/<int:pk>/audit-log/', views.gstreturn_audit_log, name='gstreturn-audit-log'),
]