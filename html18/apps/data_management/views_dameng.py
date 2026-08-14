"""达梦数据库视图：加工中心、镗铣床、操作日志、熵权法API"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from .services.dameng_service import DamengDatabaseService
from .services.boring_milling_service import BoringMillingService

class MachineParametersAPI(View):
    """加工中心参数API"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, machine_id=None):
        """获取加工中心参数"""
        try:
            if machine_id:
                result = DamengDatabaseService.get_machine_parameters(machine_id)
                return JsonResponse(result)
            else:
                return JsonResponse({
                    'success': False,
                    'message': '请指定机床ID'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取机床参数失败: {str(e)}'
            })
    
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, machine_id):
        """创建或更新加工中心参数"""
        try:
            data = json.loads(request.body)
            
            # 验证数据
            is_valid, errors = DamengDatabaseService.validate_machine_data(data)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': '数据验证失败',
                    'errors': errors
                })
            
            # 获取用户信息和IP地址
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            ip_address = self.get_client_ip(request)
            
            # 更新数据
            result = DamengDatabaseService.update_machine_parameters(
                machine_id=machine_id,
                update_data=data,
                user=user,
                ip_address=ip_address
            )
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'更新机床参数失败: {str(e)}'
            })
    
    @method_decorator(require_http_methods(["PUT"]))
    def put(self, request, machine_id):
        """更新加工中心参数（PUT方法）"""
        try:
            data = json.loads(request.body)
            
            # 验证数据
            is_valid, errors = DamengDatabaseService.validate_machine_data(data)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': '数据验证失败',
                    'errors': errors
                })
            
            # 获取用户信息和IP地址
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            ip_address = self.get_client_ip(request)
            
            # 更新数据
            result = DamengDatabaseService.update_machine_parameters(
                machine_id=machine_id,
                update_data=data,
                user=user,
                ip_address=ip_address
            )
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'更新机床参数失败: {str(e)}'
            })
    
    @method_decorator(require_http_methods(["DELETE"]))
    def delete(self, request, machine_id):
        """删除加工中心参数"""
        try:
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            ip_address = self.get_client_ip(request)
            
            result = DamengDatabaseService.delete_machine_data(
                machine_id=machine_id,
                user=user,
                ip_address=ip_address
            )
            
            if result['success']:
                from apps.evaluation.models import Machine
                from django.db import connection
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM EVALUATION_MACHINE WHERE ID = %s", [machine_id])
                except Exception as e:
                    pass
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'删除加工中心参数失败: {str(e)}'
            })
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class BoringMillingParametersAPI(View):
    """镗铣床参数API（与加工中心数据完全分离）"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, machine_id=None):
        """获取镗铣床参数列表或单个参数"""
        try:
            if machine_id:
                result = BoringMillingService.get_boring_milling_parameters(machine_id)
                return JsonResponse(result)
            else:
                result = BoringMillingService.get_all_boring_milling_machines()
                return JsonResponse(result)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取镗铣床参数失败: {str(e)}'
            })

    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, machine_id):
        """创建镗铣床参数"""
        try:
            data = json.loads(request.body)

            is_valid, errors = BoringMillingService.validate_boring_milling_data(data)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': '数据验证失败',
                    'errors': errors
                })

            user = request.user.username if request.user.is_authenticated else 'anonymous'
            ip_address = self.get_client_ip(request)

            result = BoringMillingService.update_boring_milling_parameters(
                machine_id=machine_id,
                update_data=data,
                user=user,
                ip_address=ip_address
            )

            return JsonResponse(result)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'创建镗铣床参数失败: {str(e)}'
            })

    @method_decorator(require_http_methods(["PUT"]))
    def put(self, request, machine_id):
        """更新镗铣床参数（PUT方法）"""
        try:
            data = json.loads(request.body)

            is_valid, errors = BoringMillingService.validate_boring_milling_data(data)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': '数据验证失败',
                    'errors': errors
                })

            user = request.user.username if request.user.is_authenticated else 'anonymous'
            ip_address = self.get_client_ip(request)

            result = BoringMillingService.update_boring_milling_parameters(
                machine_id=machine_id,
                update_data=data,
                user=user,
                ip_address=ip_address
            )

            return JsonResponse(result)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'更新镗铣床参数失败: {str(e)}'
            })

    @method_decorator(require_http_methods(["DELETE"]))
    def delete(self, request, machine_id):
        """删除镗铣床参数及操作日志"""
        try:
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            ip_address = self.get_client_ip(request)

            result = BoringMillingService.delete_boring_milling_data(
                machine_id=machine_id,
                user=user,
                ip_address=ip_address
            )
            
            if result['success']:
                from apps.evaluation.models import Machine
                from django.db import connection
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM EVALUATION_MACHINE WHERE ID = %s", [machine_id])
                except Exception as e:
                    pass

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'删除镗铣床参数失败: {str(e)}'
            })

    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class OperationLogsAPI(View):
    """操作日志API"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """获取操作日志列表，支持按机床ID筛选"""
        try:
            machine_id = request.GET.get('machine_id')
            limit = int(request.GET.get('limit', 100))
            
            result = DamengDatabaseService.get_operation_logs(machine_id, limit)
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取操作日志失败: {str(e)}'
            })


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """健康检查接口"""
    try:
        from .models_dameng import MachineParameters
        count = MachineParameters.objects.count()
        
        return JsonResponse({
            'success': True,
            'status': 'healthy',
            'database_connection': 'ok',
            'total_records': count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 'unhealthy',
            'database_connection': 'failed',
            'error': str(e)
        })


class EntropyWeightAPI(View):
    """信息熵权重计算结果API"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, machine_type=None):
        """获取信息熵权重计算结果，支持按机床类型筛选"""
        try:
            precision_type = request.GET.get('precision_type')
            
            if machine_type:
                result = DamengDatabaseService.get_entropy_weight_result(machine_type, precision_type)
                return JsonResponse(result)
            else:
                return JsonResponse({
                    'success': False,
                    'message': '请指定机床类型'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取信息熵权重计算结果失败: {str(e)}'
            })
    
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, machine_type):
        """保存信息熵权重计算结果"""
        try:
            data = json.loads(request.body)
            
            precision_type = data.get('precision_type')
            if not precision_type:
                return JsonResponse({
                    'success': False,
                    'message': '精度数据类型不能为空'
                })
            
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            ip_address = self.get_client_ip(request)
            
            result = DamengDatabaseService.save_entropy_weight_result(
                machine_type=machine_type,
                precision_type=precision_type,
                data=data,
                user=user,
                ip_address=ip_address
            )
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'保存信息熵权重计算结果失败: {str(e)}'
            })
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip