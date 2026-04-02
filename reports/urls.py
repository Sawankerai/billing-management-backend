from django.urls import path
from . import views

urlpatterns = [
    path('summary/',views.report_summary,name='report-summary'),
    path('performance/',views.report_performance,name='report-performance'),
    path('top-categories/', views.report_top_categories,name='report-top-categories'),
    path('top-vendors/',views.report_top_vendors,name='report-top-vendors'),
    path('breakdown/',views.report_expense_breakdown, name='report-breakdown'),
    path('full/',views.report_full,name='report-full'),
]