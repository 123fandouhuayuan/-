from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='visualization_dashboard'),
    path('charts/', views.charts_view, name='charts_view'),
    path('api/comprehensive-weight-chart-data/', views.get_comprehensive_weight_chart_data, name='get_comprehensive_weight_chart_data'),
    path('api/machine-list/', views.get_machine_list, name='get_machine_list'),
    path('api/radar-chart-data/', views.get_radar_chart_data, name='get_radar_chart_data'),
]