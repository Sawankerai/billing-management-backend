from django.contrib import admin
from django.urls import path, include
from core.views import CustomLoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

     # Authentication endpoints
     path('api/login/', CustomLoginView.as_view(), name='login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh'),

     # App endpoints
    path('api/', include('core.urls')),
    path('api/', include('invoice.urls')),
   path('api/batch/', include('inventory_batch.urls')),
   path('api/stock/', include('stock_adjustment.urls')),
]