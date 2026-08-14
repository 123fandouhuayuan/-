from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.system_settings, name='system_settings'),
    path('logs/', views.logs_view, name='logs_view'),
]