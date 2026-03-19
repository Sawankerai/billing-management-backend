from django.urls import path
from . import views

urlpatterns = [

    # ── Barcode Devices
    path('barcode/devices/', views.device_list, name='device-list'),
    path('barcode/devices/<int:pk>/', views.device_detail, name='device-detail'),
    path('barcode/devices/<int:pk>/connect/', views.device_connect, name='device-connect'),
    path('barcode/devices/<int:pk>/disconnect/', views.device_disconnect, name='device-disconnect'),

    # ── Stock Movements
    path('barcode/movements/', views.movement_list, name='movement-list'),
    path('barcode/movements/<int:pk>/', views.movement_detail, name='movement-detail'),

    # ── Actions
    path('barcode/scan/', views.barcode_scan, name='barcode-scan'),
    path('barcode/movements/transfer/', views.create_transfer, name='create-transfer'),
    path('barcode/movements/export/', views.export_movement_log, name='export-movement-log'),
]