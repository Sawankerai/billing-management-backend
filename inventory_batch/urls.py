from django.urls import path
from . import views

urlpatterns = [
    path('batches/',views.batch_list,name='batch-list'),
    path('batches/<int:pk>/',views.batch_detail,name='batch-detail'),
    path('batches/save-draft/',views.batch_save_draft, name='batch-save-draft'),
]