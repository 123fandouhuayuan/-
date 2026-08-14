from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('generate/', views.generate_report, name='generate_report'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('<int:report_id>/export/pdf/', views.export_report_pdf, name='export_report_pdf'),
    path('<int:report_id>/export/excel/', views.export_report_excel, name='export_report_excel'),
    path('api/generate/', views.api_generate_report, name='api_generate_report'),
    path('api/<int:report_id>/data/', views.api_report_data, name='api_report_data'),
    path('api/compare/', views.api_compare_reports, name='api_compare_reports'),
    path('api/delete/<int:report_id>/', views.api_delete_report, name='api_delete_report'),
]
