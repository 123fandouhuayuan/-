from django.urls import path
from . import views

urlpatterns = [
    path('machines/', views.machine_list, name='machine_list'),
    path('machines/add/', views.add_machine, name='add_machine'),
    path('machines/edit/<int:machine_id>/', views.edit_machine, name='edit_machine'),
    path('machines/delete/<int:machine_id>/', views.delete_machine, name='delete_machine'),
    path('machines/save/<int:machine_id>/', views.save_machine, name='save_machine'),
    path('machines/fix/<int:machine_id>/', views.fix_machine_model_report_number, name='fix_machine_model_report_number'),
    path('import/', views.import_data, name='import_data'),
    path('export/', views.export_data, name='export_data'),
    path('download-template/', views.download_template, name='download_template'),
    path('create-operation-log-table/', views.create_operation_log_table, name='create_operation_log_table'),
]