"""
达梦数据库URL路由配置
"""
from django.urls import path
from .views_dameng import MachineParametersAPI, OperationLogsAPI, health_check, EntropyWeightAPI, BoringMillingParametersAPI

urlpatterns = [
    # 加工中心机床参数API
    path('api/machine-parameters/<int:machine_id>/', MachineParametersAPI.as_view(), name='machine_parameters_api'),
    path('api/machine-parameters/', MachineParametersAPI.as_view(), name='machine_parameters_list_api'),
    
    # 镗铣床独立参数API
    path('api/boring-milling-parameters/<int:machine_id>/', BoringMillingParametersAPI.as_view(), name='boring_milling_parameters_api'),
    path('api/boring-milling-parameters/', BoringMillingParametersAPI.as_view(), name='boring_milling_parameters_list_api'),
    
    # 操作日志API
    path('api/operation-logs/', OperationLogsAPI.as_view(), name='operation_logs_api'),
    
    # 信息熵权重计算结果API - 使用机床类型
    path('api/entropy-weight/<str:machine_type>/', EntropyWeightAPI.as_view(), name='entropy_weight_api'),
    
    # 健康检查
    path('api/health-check/', health_check, name='dameng_health_check'),
]
