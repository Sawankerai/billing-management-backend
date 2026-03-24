from django.urls import path
from . import views

urlpatterns = [
    path('', views.credit_note_list, name='credit-note-list'),
    path('stats/', views.credit_note_stats, name='credit-note-stats'),
    path('<int:pk>/', views.credit_note_detail, name='credit-note-detail'),
    path('<int:pk>/approve/', views.approve_credit_note, name='credit-note-approve'),
    path('<int:pk>/issue/', views.issue_credit_note, name='credit-note-issue'),
    path('<int:pk>/cancel/', views.cancel_credit_note, name='credit-note-cancel'),
]