from django.urls import path
from . import views

urlpatterns = [
    path('recurring-expenses/',
         views.recurring_expense_list,   name='recurring-expense-list'),

    path('recurring-expenses/<int:pk>/',
         views.recurring_expense_detail, name='recurring-expense-detail'),
]