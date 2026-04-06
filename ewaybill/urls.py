from django.urls import path
from . import views

urlpatterns = [

    path('ewaybills/stats/',views.ewaybill_stats,name='ewaybill-stats'),

    path('ewaybills/',views.ewaybill_list,name='ewaybill-list'),

    path('ewaybills/<int:pk>/',views.ewaybill_detail,name='ewaybill-detail'),

    path('ewaybills/<int:pk>/generate/',views.generate_ewaybill, name='ewaybill-generate'),
    path('ewaybills/<int:pk>/close/',views.close_ewaybill,name='ewaybill-close'),
    path('ewaybills/<int:pk>/cancel/',views.cancel_ewaybill,name='ewaybill-cancel'),
    path('ewaybills/<int:pk>/update-vehicle/',views.update_vehicle,name='ewaybill-update-vehicle'),

    path('ewaybills/<int:pk>/audit-log/',views.ewaybill_audit_log, name='ewaybill-audit-log'),
]