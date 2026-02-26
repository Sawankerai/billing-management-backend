from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()


urlpatterns = [
   
    path('admin/', admin.site.urls),
     path('api/', include(router.urls)),

   
    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh'),

  
    path('api/', include('core.urls')),
    
    path('api/token/', obtain_auth_token),
]