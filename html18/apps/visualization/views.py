from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.data_management.services.dameng_service import DamengDatabaseService
from apps.accounts.models import UserProfile
from apps.evaluation.models import Machine

@login_required
def dashboard_view(request):
    """可视化仪表板"""
    user_profile = UserProfile.objects.select_related('user').get(user=request.user)
    is_admin = user_profile.is_admin()
    
    context = {
        'title': '可视化分析',
        'page_title': '数据可视化仪表板',
        'is_admin': is_admin,
    }
    return render(request, 'visualization/dashboard.html', context)

@login_required
def charts_view(request):
    """图表展示"""
    user_profile = UserProfile.objects.select_related('user').get(user=request.user)
    is_admin = user_profile.is_admin()
    
    context = {
        'title': '图表分析',
        'page_title': '图表分析',
        'is_admin': is_admin,
    }
    return render(request, 'visualization/charts.html', context)

@login_required
def get_comprehensive_weight_chart_data(request):
    """API: 获取精度综合权重计算结果图表数据"""
    if request.method == 'GET':
        try:
            machine_type = request.GET.get('machine_type', '')
            
            # 获取用户角色
            try:
                user_profile = request.user.userprofile
                is_admin = user_profile.is_admin()
            except Exception:
                is_admin = False
            
            # 获取可见的机床ID
            if is_admin:
                # 管理员只能看到已保存的机床（admin_saved=True）
                # 只有在机床管理界面点击保存后，数据才会在可视化分析中显示
                visible_machine_ids = set(Machine.objects.filter(
                    admin_saved=True
                ).values_list('id', flat=True))
            else:
                # 普通用户可以看到自己创建的机床
                visible_machine_ids = set(Machine.objects.filter(
                    created_by=request.user
                ).values_list('id', flat=True))
            
            result = DamengDatabaseService.get_all_comprehensive_weight_results()
            
            if not result['success']:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'data': []
                })
            
            data = result['data']
            
            # 过滤：仅保留可见机床的数据
            data = [item for item in data if item['machine_id'] in visible_machine_ids]
            
            if machine_type:
                data = [item for item in data if item['machine_type'] == machine_type]
            
            chart_data = []
            for item in data:
                chart_data.append({
                    'id': item['id'],
                    'report_number': item['report_number'],
                    'machine_id': item['machine_id'],
                    'machine_model': item['machine_model'],
                    'machine_type': item['machine_type'],
                    'comprehensive_score': float(item['comprehensive_score']),
                    'precision_score': float(item['precision_score']),
                    'performance_score': float(item.get('performance_score', 0)),
                    'reliability_score': float(item.get('reliability_score', 0)),
                    'intelligence_score': float(item.get('intelligence_score', 0)),
                    'green_score': float(item.get('green_score', 0)),
                    'total_weight': float(item['total_weight']),
                    'calculated_at': item['calculated_at'],
                    'version': item['version']
                })
            
            chart_data.sort(key=lambda x: x['machine_id'])
            
            return JsonResponse({
                'success': True,
                'data': chart_data,
                'count': len(chart_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'data': []
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method', 'data': []})

@login_required
def get_machine_list(request):
    """API: 获取机床列表（用于雷达图选择）"""
    if request.method == 'GET':
        try:
            machine_type = request.GET.get('machine_type', '')
            
            # 获取用户角色
            try:
                user_profile = request.user.userprofile
                is_admin = user_profile.is_admin()
            except Exception:
                is_admin = False
            
            # 获取可见的机床ID
            if is_admin:
                visible_machine_ids = set(Machine.objects.filter(
                    admin_saved=True
                ).values_list('id', flat=True))
            else:
                visible_machine_ids = set(Machine.objects.filter(
                    created_by=request.user
                ).values_list('id', flat=True))
            
            result = DamengDatabaseService.get_all_comprehensive_weight_results()
            
            if not result['success']:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'data': []
                })
            
            data = result['data']
            
            # 过滤：仅保留可见机床的数据
            data = [item for item in data if item['machine_id'] in visible_machine_ids]
            
            if machine_type:
                data = [item for item in data if item['machine_type'] == machine_type]
            
            machine_list = []
            seen_machine_ids = set()
            
            for item in data:
                machine_id = item['machine_id']
                if machine_id not in seen_machine_ids:
                    seen_machine_ids.add(machine_id)
                    machine_list.append({
                        'id': machine_id,
                        'name': item['machine_model'],
                        'report_number': item['report_number'],
                        'machine_type': item['machine_type']
                    })
            
            machine_list.sort(key=lambda x: x['id'])
            
            return JsonResponse({
                'success': True,
                'data': machine_list,
                'count': len(machine_list)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'data': []
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method', 'data': []})

@login_required
def get_radar_chart_data(request):
    """API: 获取雷达图数据（五维度评分，仅显示管理员已保存的机床）"""
    if request.method == 'GET':
        try:
            report_number = request.GET.get('report_number', '')
            
            if not report_number:
                return JsonResponse({
                    'success': False,
                    'error': 'Report number is required',
                    'data': None
                })
            
            # 仅查询管理员已保存的机床ID
            admin_saved_machine_ids = set(Machine.objects.filter(
                admin_saved=True
            ).values_list('id', flat=True))
            
            result = DamengDatabaseService.get_all_comprehensive_weight_results()
            
            if not result['success']:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'data': None
                })
            
            data = result['data']
            
            # 过滤：仅保留admin_saved=True的机床数据
            data = [item for item in data if item['machine_id'] in admin_saved_machine_ids]
            
            machine_data = None
            for item in data:
                if str(item.get('report_number', '')) == str(report_number):
                    machine_data = item
                    break
            
            if not machine_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Report not found',
                    'data': None
                })
            
            radar_data = {
                'machine_id': machine_data['machine_id'],
                'machine_name': machine_data.get('machine_model', machine_data.get('machine_name', '')),
                'report_number': machine_data.get('report_number', ''),
                'machine_type': machine_data.get('machine_type', ''),
                'precision_score': float(machine_data.get('precision_score', 0)),
                'performance_score': float(machine_data.get('performance_score', 0)),
                'reliability_score': float(machine_data.get('reliability_score', 0)),
                'intelligence_score': float(machine_data.get('intelligence_score', 0)),
                'green_score': float(machine_data.get('green_score', 0)),
                'comprehensive_score': float(machine_data['comprehensive_score']),
                'total_weight': float(machine_data['total_weight']),
                'calculated_at': machine_data.get('calculated_at', ''),
                'version': machine_data.get('version', 1)
            }
            
            return JsonResponse({
                'success': True,
                'data': radar_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'data': None
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method', 'data': None})