from django.urls import path
from . import views

urlpatterns = [
    path('',views.payment_list,name='payment-list'),
    path('stats/',views.payment_stats,name='payment-stats'),
    path('exceptions/',views.payment_exceptions, name='payment-exceptions'),
    path('<int:pk>/',views.payment_detail,name='payment-detail'),
    path('<int:pk>/apply/',views.apply_payment,name='payment-apply'),
    path('<int:pk>/fail/',views.fail_payment,name='payment-fail'),
    path('<int:pk>/cancel/',views.cancel_payment,name='payment-cancel'),
]