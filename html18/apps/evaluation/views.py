from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from apps.accounts.decorators import get_user_queryset
import json
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@login_required
def evaluation_dashboard(request):
    """评价总览"""
    from .models import Evaluation, UserEvaluationResult, Machine
    from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
    from django.db.models import Case, When, Value, IntegerField
    from apps.accounts.models import UserProfile
    
    user_profile = UserProfile.objects.select_related('user').get(user=request.user)
    is_admin = user_profile.is_admin()
    
    comprehensive_results = []
    
    if is_admin:
        comprehensive_results = list(ComprehensiveWeightResultDameng.objects.all().order_by('-updated_at')[:10])
    else:
        user_machine_ids = Machine.objects.filter(created_by=request.user).values_list('id', flat=True)
        dameng_results = list(ComprehensiveWeightResultDameng.objects.filter(
            machine_id__in=user_machine_ids
        ).order_by('-updated_at')[:10])
        
        user_results = list(UserEvaluationResult.objects.filter(
            machine_id__in=user_machine_ids
        ).select_related('machine', 'evaluator').order_by('-updated_at')[:10])
        
        for result in dameng_results:
            result.machine_name = result.machine_model
            result.report_number = getattr(result, 'report_number', '')
        
        for result in user_results:
            result.report_number = f"USER-{result.id:05d}"
            result.machine_name = result.machine.name if result.machine else ''
            result.comprehensive_score = result.total_score
            result.updated_at = result.updated_at
        
        existing_machine_ids = set(r.machine_id for r in dameng_results)
        for result in user_results:
            if result.machine_id not in existing_machine_ids:
                comprehensive_results.append(result)
        
        comprehensive_results = dameng_results + comprehensive_results
    
    machine_ids = [result.machine_id for result in comprehensive_results if result.machine_id]
    machines_map = {machine.id: machine for machine in Machine.objects.filter(id__in=machine_ids).select_related('created_by')}
    
    for result in comprehensive_results:
        machine = machines_map.get(result.machine_id)
        result.machine_name = machine.name if machine else getattr(result, 'machine_name', result.machine_model if hasattr(result, 'machine_model') else '')
        # 添加上传用户信息
        if machine and machine.created_by:
            result.upload_user = machine.created_by.get_full_name() or machine.created_by.username
        elif hasattr(result, 'evaluator') and result.evaluator:
            result.upload_user = result.evaluator
        else:
            result.upload_user = '未知'
    
    context = {
        'title': '评价总览',
        'welcome_message': '欢迎使用质量评价系统',
        'evaluations': comprehensive_results,
        'is_admin': is_admin,
    }
    return render(request, 'evaluation/dashboard.html', context)


@login_required
def evaluation_wizard(request):
    """评价向导"""
    from .models import Machine
    from django.db.models import Q
    from apps.accounts.models import UserProfile
    
    # 根据用户角色过滤机床（使用select_related优化查询）
    user_profile = UserProfile.objects.select_related('user').get(user=request.user)
    if user_profile.is_admin():
        # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床
        machines = Machine.objects.filter(
            Q(created_by=request.user) | Q(admin_saved=True)
        ).distinct().select_related('created_by')
    else:
        # 普通用户只能看到自己创建的机床
        machines = Machine.objects.filter(created_by=request.user).select_related('created_by')
    
    context = {
        'title': '质量评价向导',
        'steps': ['选择机床', '分数计算', '查看报告'],
        'machines': machines
    }
    return render(request, 'evaluation/evaluation_wizard.html', context)




@login_required
def run_evaluation(request):
    """运行评价"""
    from .models import Machine
    
    if request.method == 'POST':
        # 获取用户输入的参数
        machine_id = request.POST.get('machine_id')
        evaluation_type = request.POST.get('evaluation_type')
        method = request.POST.get('method')
        
        # 这里处理评价逻辑
        messages.success(request, '评价任务已提交')
        return redirect('evaluation_dashboard')

    # 根据用户角色过滤机床
    user_profile = request.user.userprofile
    if user_profile.is_admin():
        # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床
        machines = Machine.objects.filter(
            Q(created_by=request.user) | Q(admin_saved=True)
        ).distinct()
    else:
        # 普通用户只能看到自己创建的机床
        machines = Machine.objects.filter(created_by=request.user)
    
    context = {
        'title': '运行评价',
        'machines': machines
    }
    return render(request, 'evaluation/run_evaluation.html', context)


@login_required
def run_evaluation_pro(request):
    """运行评价（专家版）"""
    from .models import Machine
    
    if request.method == 'POST':
        # 获取用户输入的参数
        machine_id = request.POST.get('machine_id')
        evaluation_type = request.POST.get('evaluation_type')
        method = request.POST.get('method')
        
        # 这里处理评价逻辑
        messages.success(request, '评价任务已提交')
        return redirect('evaluation_dashboard')

    # 根据用户角色过滤机床
    user_profile = request.user.userprofile
    if user_profile.is_admin():
        # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床
        machines = Machine.objects.filter(
            Q(created_by=request.user) | Q(admin_saved=True)
        ).distinct()
    else:
        # 普通用户只能看到自己创建的机床
        machines = Machine.objects.filter(created_by=request.user)
    
    context = {
        'title': '运行评价（专家版）',
        'machines': machines
    }
    return render(request, 'evaluation/run_evaluation_pro.html', context)


@login_required
def run_evaluation_user(request):
    """运行评价（用户版）- 统一入口，支持加工中心和镗铣床"""
    from apps.data_management.services.dameng_service import DamengDatabaseService
    from apps.system.models import LicenseManagement
    
    if request.method == 'POST':
        machine_id = request.POST.get('machine_id')
        evaluation_type = request.POST.get('evaluation_type')
        method = request.POST.get('method')
        
        messages.success(request, '评价任务已提交')
        return redirect('evaluation_dashboard')

    machine_id = request.GET.get('machine_id')
    machine_type = request.GET.get('machine_type', 'machining_center')
    
    is_boring_milling = machine_type == 'boring_milling_machine'
    
    if is_boring_milling:
        try:
            license = LicenseManagement.objects.get(
                license_type='boring_milling_machine',
                is_enabled=True,
                status='active'
            )
            if not license.is_valid():
                messages.error(request, '镗铣床许可未激活或已过期，请联系系统管理员。')
                return redirect('evaluation_wizard')
        except LicenseManagement.DoesNotExist:
            pass
        except Exception as e:
            print(f"许可管理表未创建，允许访问镗铣床界面: {e}")
    
    machines_result = DamengDatabaseService.get_all_machines()
    machines = []
    if machines_result['success']:
        machines = machines_result['data']
    
    if machine_id:
        try:
            machine_result = DamengDatabaseService.get_machine_parameters(machine_id)
            if machine_result['success']:
                machine = machine_result['data']
                
                license_enabled = False
                if machine['machine_type'] == 'machining_center':
                    license_enabled = True
                elif machine['machine_type'] == 'boring_milling_machine':
                    license_enabled = True
                else:
                    license_enabled = False
                
                if not license_enabled:
                    messages.error(request, f'抱歉，当前机床类型（{machine.get("machine_type", "未知")}）的许可未启用。请联系系统管理员。')
                    return redirect('evaluation_wizard')
                    
        except Exception as e:
            messages.error(request, f'抱歉，指定的机床（ID: {machine_id}）不存在。')
            return redirect('evaluation_wizard')
    
    path = request.GET.get('path', '')
    
    user_role = 'user'
    is_admin = False
    is_expert = False
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            user_role = user_profile.role
            is_admin = user_profile.is_admin()
            is_expert = user_profile.is_expert()
        except Exception as e:
            logger.warning(f"获取用户角色失败: {str(e)}")
    
    machine_type_display = '镗铣床' if is_boring_milling else '加工中心'
    
    context = {
        'title': f'运行评价（用户版）- {machine_type_display}',
        'machines': machines,
        'path': path,
        'machine_type': machine_type,
        'is_boring_milling': is_boring_milling,
        'user_role': user_role,
        'is_admin': is_admin,
        'is_expert': is_expert,
        'resource_section_weight': 0.4,
        'energy_section_weight': 0.6,
        'cutting_fluid_weight': 0.1,
        'lubricant_weight': 0.1,
        'lightweight_weight': 0.1,
        'energy_weight': 0.1,
        'workpiece_weight': 0.1,
        'volume_weight': 0.1,
        'standby_weight': 0.1,
        'idle_weight': 0.1,
        'cutting_weight': 0.1,
        'cutting_energy_weight': 0.1
    }
    
    try:
        from .models import AHPMatrix
        ahp_green = AHPMatrix.objects.filter(path='绿色化').first()
        if ahp_green and ahp_green.weights:
            weights = ahp_green.weights
            if len(weights) >= 2:
                context['resource_section_weight'] = weights[0]
                context['energy_section_weight'] = weights[1]
            elif len(weights) == 1:
                context['resource_section_weight'] = weights[0]
                context['energy_section_weight'] = 1 - weights[0]
        
        ahp_resource = AHPMatrix.objects.filter(path='绿色化/资源循环与耗材').first()
        if ahp_resource and ahp_resource.weights:
            resource_weights = ahp_resource.weights
            if len(resource_weights) >= 3:
                context['cutting_fluid_weight'] = resource_weights[0]
                context['lubricant_weight'] = resource_weights[1]
                context['lightweight_weight'] = resource_weights[2]
            elif len(resource_weights) == 2:
                context['cutting_fluid_weight'] = resource_weights[0]
                context['lubricant_weight'] = resource_weights[1]
                context['lightweight_weight'] = 1 - resource_weights[0] - resource_weights[1]
        
        ahp_energy = AHPMatrix.objects.filter(path='绿色化/能源-能效').first()
        if ahp_energy and ahp_energy.weights:
            energy_weights = ahp_energy.weights
            if len(energy_weights) >= 7:
                context['energy_weight'] = energy_weights[0]
                context['workpiece_weight'] = energy_weights[1]
                context['volume_weight'] = energy_weights[2]
                context['standby_weight'] = energy_weights[3]
                context['idle_weight'] = energy_weights[4]
                context['cutting_weight'] = energy_weights[5]
                context['cutting_energy_weight'] = energy_weights[6]
        
        ahp_perf = AHPMatrix.objects.filter(path='性能').first()
        if ahp_perf and ahp_perf.weights:
            perf_weights = ahp_perf.weights
            if len(perf_weights) >= 4:
                context['machining_section_weight'] = perf_weights[0]
                context['stiffness_section_weight'] = perf_weights[1]
                context['operation_section_weight'] = perf_weights[2]
                context['load_section_weight'] = perf_weights[3]
            elif len(perf_weights) == 3:
                context['machining_section_weight'] = perf_weights[0]
                context['stiffness_section_weight'] = perf_weights[1]
                context['operation_section_weight'] = perf_weights[2]
                context['load_section_weight'] = 1 - perf_weights[0] - perf_weights[1] - perf_weights[2]
        
        # 可靠性权重
        ahp_reliability = AHPMatrix.objects.filter(path='可靠性').first()
        if ahp_reliability and ahp_reliability.weights:
            reliability_weights = ahp_reliability.weights
            if len(reliability_weights) >= 7:
                context['mtbf_weight'] = reliability_weights[0]
                context['mttr_weight'] = reliability_weights[1]
                context['availability_weight'] = reliability_weights[2]
                context['failure_rate_weight'] = reliability_weights[3]
                context['consistency_weight'] = reliability_weights[4]
                context['precision_keep_weight'] = reliability_weights[5]
                context['mttf_weight'] = reliability_weights[6]
        
        ahp_machining = AHPMatrix.objects.filter(path='性能/加工性能').first()
        if ahp_machining and ahp_machining.weights:
            machining_weights = ahp_machining.weights
            if len(machining_weights) >= 2:
                context['dispersion_weight'] = machining_weights[0]
                context['efficiency_weight'] = machining_weights[1]
            elif len(machining_weights) == 1:
                context['dispersion_weight'] = machining_weights[0]
                context['efficiency_weight'] = 1 - machining_weights[0]
        
        ahp_efficiency = AHPMatrix.objects.filter(path='性能/加工性能/加工效率').first()
        if ahp_efficiency and ahp_efficiency.weights:
            efficiency_weights = ahp_efficiency.weights
            if len(efficiency_weights) >= 3:
                context['efficiency_spindle_weight'] = efficiency_weights[0]
                context['efficiency_fast_speed_weight'] = efficiency_weights[1]
                context['efficiency_feed_speed_weight'] = efficiency_weights[2]
            elif len(efficiency_weights) == 2:
                context['efficiency_spindle_weight'] = efficiency_weights[0]
                context['efficiency_fast_speed_weight'] = efficiency_weights[1]
                context['efficiency_feed_speed_weight'] = 1 - efficiency_weights[0] - efficiency_weights[1]
        
        ahp_stiffness = AHPMatrix.objects.filter(path='性能/机床刚度').first()
        if ahp_stiffness and ahp_stiffness.weights:
            stiffness_weights = ahp_stiffness.weights
            if len(stiffness_weights) >= 1:
                context['static_stiffness_weight'] = stiffness_weights[0]
        else:
            context['static_stiffness_weight'] = 1.0
        
        ahp_static_stiffness = AHPMatrix.objects.filter(path='性能/机床刚度/静刚度').first()
        if ahp_static_stiffness and ahp_static_stiffness.weights:
            static_stiffness_weights = ahp_static_stiffness.weights
            if len(static_stiffness_weights) >= 2:
                context['static_stiffness_radial_weight'] = static_stiffness_weights[0]
                context['static_stiffness_axial_weight'] = static_stiffness_weights[1]
            elif len(static_stiffness_weights) == 1:
                context['static_stiffness_radial_weight'] = static_stiffness_weights[0]
                context['static_stiffness_axial_weight'] = 1 - static_stiffness_weights[0]
        else:
            context['static_stiffness_radial_weight'] = 0.5
            context['static_stiffness_axial_weight'] = 0.5
        
        ahp_operation = AHPMatrix.objects.filter(path='性能/运行性能').first()
        if ahp_operation and ahp_operation.weights:
            operation_weights = ahp_operation.weights
            if len(operation_weights) >= 4:
                context['spindle_weight'] = operation_weights[0]
                context['noise_weight'] = operation_weights[1]
                context['current_stability_weight'] = operation_weights[2]
                context['thermal_deformation_weight'] = operation_weights[3]
            elif len(operation_weights) == 3:
                context['spindle_weight'] = operation_weights[0]
                context['noise_weight'] = operation_weights[1]
                context['current_stability_weight'] = operation_weights[2]
                context['thermal_deformation_weight'] = 1 - operation_weights[0] - operation_weights[1] - operation_weights[2]
        
        ahp_load = AHPMatrix.objects.filter(path='性能/负荷能力').first()
        if ahp_load and ahp_load.weights:
            load_weights = ahp_load.weights
            if len(load_weights) >= 3:
                context['spindle_load_weight'] = load_weights[0]
                context['max_load_weight'] = load_weights[1]
                context['vibration_resistance_weight'] = load_weights[2]
            elif len(load_weights) == 2:
                context['spindle_load_weight'] = load_weights[0]
                context['max_load_weight'] = load_weights[1]
                context['vibration_resistance_weight'] = 1 - load_weights[0] - load_weights[1]
        
        ahp_spindle_load = AHPMatrix.objects.filter(path='性能/负荷能力/主轴负载能力').first()
        if ahp_spindle_load and ahp_spindle_load.weights:
            spindle_load_weights = ahp_spindle_load.weights
            if len(spindle_load_weights) >= 2:
                context['spindle_load_power_weight'] = spindle_load_weights[0]
                context['spindle_load_torque_weight'] = spindle_load_weights[1]
            elif len(spindle_load_weights) == 1:
                context['spindle_load_power_weight'] = spindle_load_weights[0]
                context['spindle_load_torque_weight'] = 1 - spindle_load_weights[0]
        else:
            context['spindle_load_power_weight'] = 0.5
            context['spindle_load_torque_weight'] = 0.5
        
        ahp_current_stability = AHPMatrix.objects.filter(path='性能/运行性能/电流稳定性').first()
        if ahp_current_stability and ahp_current_stability.weights:
            stability_weights = ahp_current_stability.weights
            if len(stability_weights) >= 3:
                context['current_stability_spindle_weight'] = stability_weights[0]
                context['current_stability_linear_axis_weight'] = stability_weights[1]
                context['current_stability_power_weight'] = stability_weights[2]
            elif len(stability_weights) == 2:
                context['current_stability_spindle_weight'] = stability_weights[0]
                context['current_stability_linear_axis_weight'] = stability_weights[1]
                context['current_stability_power_weight'] = 1 - stability_weights[0] - stability_weights[1]
        else:
            context['current_stability_spindle_weight'] = 0.37
            context['current_stability_linear_axis_weight'] = 0.315
            context['current_stability_power_weight'] = 0.315
        
        ahp_thermal_deformation = AHPMatrix.objects.filter(path='性能/运行性能/主轴温升热变形').first()
        if ahp_thermal_deformation and ahp_thermal_deformation.weights:
            thermal_weights = ahp_thermal_deformation.weights
            if len(thermal_weights) >= 2:
                context['thermal_deformation_radial_weight'] = thermal_weights[0]
                context['thermal_deformation_axial_weight'] = thermal_weights[1]
            elif len(thermal_weights) == 1:
                context['thermal_deformation_radial_weight'] = thermal_weights[0]
                context['thermal_deformation_axial_weight'] = 1 - thermal_weights[0]
        else:
            context['thermal_deformation_radial_weight'] = 0.5
            context['thermal_deformation_axial_weight'] = 0.5
    except Exception as e:
        logger.warning(f"获取绿色化板块权重失败: {str(e)}")
    
    return render(request, 'evaluation/run_evaluation_user.html', context)


@login_required
def api_run_evaluation(request):
    """API: 运行评价"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 这里实现API评价逻辑
            return JsonResponse({
                'success': True,
                'message': '评价成功',
                'data': {
                    'score': 85.5,
                    'grade': 'A',
                    'weights': {}
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def save_performance_score(request):
    """API: 保存性能得分 - 支持管理员数据库存储和普通用户本地存储"""
    if request.method == 'POST':
        try:
            from .models import Machine
            from apps.data_management.services.dameng_service import DamengDatabaseService
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}, 请求体: {request.body[:200]}")
                return JsonResponse({'success': False, 'error': f'JSON格式错误: {str(e)}'})
            
            machine_id = data.get('machine_id')
            performance_score = data.get('performance_score')
            
            # 验证machine_id参数（所有用户都需要提供）
            if not machine_id:
                return JsonResponse({'success': False, 'error': 'machine_id参数不能为空'})
            
            # 转换machine_id为整数
            try:
                machine_id = int(machine_id)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'machine_id必须是整数'})
            
            # 验证performance_score参数
            if performance_score is None or performance_score == '':
                return JsonResponse({'success': False, 'error': 'performance_score参数不能为空'})
            
            try:
                performance_score = float(performance_score)
                # [FIX] 修改为百分制评分标准（60-100分）
                if performance_score < 60 or performance_score > 100:
                    return JsonResponse({'success': False, 'error': '性能得分必须在60-100之间（百分制）'})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': '性能得分必须是数字'})
            
            # 获取各子指标得分（可选）
            dispersion_score = data.get('dispersion_score', 0)
            efficiency_score = data.get('efficiency_score', 0)
            static_stiffness_score = data.get('static_stiffness_score', 0)
            spindle_score = data.get('spindle_score', 0)
            noise_score = data.get('noise_score', 0)
            current_stability_score = data.get('current_stability_score', 0)
            thermal_deformation_score = data.get('thermal_deformation_score', 0)
            spindle_load_score = data.get('spindle_load_score', 0)
            max_load_score = data.get('max_load_score', 0)
            vibration_resistance_score = data.get('vibration_resistance_score', 0)
            
            # 获取用户角色
            try:
                user_profile = request.user.userprofile
                is_admin = user_profile.is_admin()
                is_expert = user_profile.is_expert()
            except Exception as e:
                logger.error(f"获取用户角色失败: {str(e)}")
                return JsonResponse({'success': False, 'error': f'获取用户角色失败: {str(e)}'})
            
            # 所有用户：保存到数据库
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
            
            # 保存到达梦数据库
            dameng_result = DamengDatabaseService.save_performance_score(
                machine_type=machine.machine_type,
                report_number=machine.report_number or f"RPT_{machine.id}",
                machine_id=machine.id,
                machine_model=machine.model or machine.name or f"Machine_{machine.id}",
                performance_score=performance_score,
                dispersion_score=dispersion_score,
                efficiency_score=efficiency_score,
                static_stiffness_score=static_stiffness_score,
                spindle_score=spindle_score,
                noise_score=noise_score,
                current_stability_score=current_stability_score,
                thermal_deformation_score=thermal_deformation_score,
                spindle_load_score=spindle_load_score,
                max_load_score=max_load_score,
                vibration_resistance_score=vibration_resistance_score,
                user=request.user.username if request.user.is_authenticated else 'unknown',
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            
            if dameng_result['success']:
                logger.info(f"用户 {request.user.username} (角色: {user_profile.role}) 成功保存性能得分: {performance_score}分 (机床ID: {machine_id}, 存储类型: 数据库)")
                return JsonResponse({
                    'success': True,
                    'message': '性能得分保存成功',
                    'result_id': dameng_result['data']['id'],
                    'performance_score': float(performance_score),
                    'storage_type': 'database',
                    'operation': dameng_result['data']['operation']
                })
            else:
                logger.error(f"用户 {request.user.username} (角色: {user_profile.role}) 保存性能得分失败: {dameng_result['message']}")
                return JsonResponse({
                    'success': False,
                    'error': f'保存到达梦数据库失败: {dameng_result["message"]}'
                })
                
        except Exception as e:
            logger.error(f"保存性能得分异常: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_user_evaluation_result(request):
    """API: 获取用户评价结果 - 用于综合权重计算"""
    if request.method == 'GET':
        try:
            from .models import UserEvaluationResult, Machine
            
            machine_id = request.GET.get('machine_id')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})
            
            # 获取机床对象
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': '机床不存在'})
            
            # 获取用户评价结果
            evaluation_result = UserEvaluationResult.objects.filter(machine=machine).first()
            
            if not evaluation_result:
                return JsonResponse({'success': False, 'error': '未找到该机床的用户评价结果'})
            
            # 构建指标得分映射
            indicator_scores = {}
            
            # 辅助函数：确保分数至少保留4位小数
            def ensure_four_decimal_places(value):
                if value is None:
                    return 0.0
                return round(float(value), 4)
            
            # 几何精度
            # 根据机床类型决定工作台精度的指标名称
            machine_type = machine.machine_type
            is_boring_milling = machine_type == 'boring_milling_machine'
            
            worktable_indicators = {
                    '平面度': ensure_four_decimal_places(evaluation_result.worktable_flatness_min_score),
                    'T型槽平行度': ensure_four_decimal_places(evaluation_result.worktable_tslot_min_score)
                }
            if is_boring_milling:
                worktable_indicators['平行度'] = ensure_four_decimal_places(evaluation_result.worktable_parallelism_min_score)
            else:
                worktable_indicators['直线度'] = ensure_four_decimal_places(evaluation_result.worktable_straightness_min_score)
            
            indicator_scores['几何精度'] = {
                '进给轴精度': {
                    '直线度': ensure_four_decimal_places(evaluation_result.feed_axis_straightness_min_score),
                    '平行度': ensure_four_decimal_places(evaluation_result.feed_axis_parallelism_min_score),
                    '角度误差': ensure_four_decimal_places(evaluation_result.feed_axis_angle_min_score),
                    '垂直度': ensure_four_decimal_places(evaluation_result.feed_axis_perpendicularity_min_score)
                },
                '工作台精度': worktable_indicators,
                '主轴精度': {
                    '圆度': ensure_four_decimal_places(evaluation_result.roundness_min_score),
                    '同轴度': ensure_four_decimal_places(evaluation_result.coaxiality_min_score),
                    '主轴径向跳动': ensure_four_decimal_places(evaluation_result.spindle_radial_runout_min_score),
                    '主轴端面跳动': ensure_four_decimal_places(evaluation_result.spindle_end_runout_min_score),
                    '主轴轴向窜动': ensure_four_decimal_places(evaluation_result.spindle_axial_runout_min_score)
                },
                '刀库精度': {
                    '刀库定位精度': ensure_four_decimal_places(evaluation_result.tool_magazine_positioning_min_score),
                    '刀库重复定位精度': ensure_four_decimal_places(evaluation_result.tool_magazine_repeatability_min_score)
                }
            }
            
            # 位置精度
            indicator_scores['位置精度'] = {
                '重复定位精度': ensure_four_decimal_places(evaluation_result.position_repeatability_min_score),
                '定位精度': ensure_four_decimal_places(evaluation_result.position_positioning_min_score),
                '平均位置偏移': ensure_four_decimal_places(evaluation_result.position_offset_min_score),
                '定位系统偏差': ensure_four_decimal_places(evaluation_result.position_deviation_min_score),
                '最小分辨率': ensure_four_decimal_places(evaluation_result.position_resolution_min_score),
                '反向间隙(差值)': ensure_four_decimal_places(evaluation_result.position_backlash_min_score)
            }
            
            # 加工精度
            indicator_scores['加工精度'] = {
                '微观几何形状误差': {
                    '表面粗糙度': ensure_four_decimal_places(evaluation_result.machining_surface_roughness_min_score)
                },
                '加工分散性': {
                    '加工工序能力': ensure_four_decimal_places(evaluation_result.machining_process_capability_min_score)
                },
                '工件几何精度': {
                    '尺寸精度': ensure_four_decimal_places(evaluation_result.machining_dimension_min_score),
                    '形状精度': ensure_four_decimal_places(evaluation_result.machining_geometry_min_score)
                }
            }
            
            # 辅助函数：确保字典中的所有数值至少保留4位小数
            def ensure_dict_four_decimal_places(data):
                if not isinstance(data, dict):
                    return ensure_four_decimal_places(data)
                result = {}
                for key, value in data.items():
                    if isinstance(value, dict):
                        result[key] = ensure_dict_four_decimal_places(value)
                    elif isinstance(value, list):
                        result[key] = [ensure_four_decimal_places(v) for v in value]
                    else:
                        result[key] = ensure_four_decimal_places(value)
                return result
            
            # 运动精度
            # 检查是否有运动精度的详细数据（JSON格式）
            if evaluation_result.motion_accuracy and isinstance(evaluation_result.motion_accuracy, dict):
                # 使用JSON格式的详细数据
                motion_accuracy = evaluation_result.motion_accuracy
                indicator_scores['运动精度'] = {
                    '主轴运动精度': ensure_dict_four_decimal_places(motion_accuracy.get('主轴运动精度', {})),
                    '多轴联动精度': ensure_dict_four_decimal_places(motion_accuracy.get('多轴联动精度', {})),
                    '传动精度': ensure_dict_four_decimal_places(motion_accuracy.get('传动精度', {})),
                    '热误差': ensure_dict_four_decimal_places(motion_accuracy.get('热误差', {})),
                    '磨损精度': ensure_dict_four_decimal_places(motion_accuracy.get('磨损精度', {}))
                }
            else:
                # 使用单个数值（兼容旧数据）
                indicator_scores['运动精度'] = {
                    '主轴运动精度': ensure_four_decimal_places(evaluation_result.motion_spindle_min_score),
                    '多轴联动精度': ensure_four_decimal_places(evaluation_result.motion_multi_axis_min_score),
                    '传动精度': ensure_four_decimal_places(evaluation_result.motion_transmission_min_score),
                    '热误差': ensure_four_decimal_places(evaluation_result.motion_thermal_min_score),
                    '磨损精度': ensure_four_decimal_places(evaluation_result.motion_wear_min_score)
                }
            
            # 获取所有机床列表，建立机床与组别的映射关系
            # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床（admin_saved=True）
            # 普通用户只能看到自己创建的机床
            from django.db.models import Q
            user_profile = request.user.userprofile
            if user_profile.is_admin():
                all_machines = Machine.objects.filter(
                    Q(created_by=request.user) | Q(admin_saved=True)
                ).distinct().order_by('id')
            else:
                all_machines = Machine.objects.filter(created_by=request.user).order_by('id')
            machine_group_mapping = {}
            for index, m in enumerate(all_machines, start=1):
                machine_group_mapping[m.id] = index
            
            # 获取当前机床的组别序号
            current_group_number = machine_group_mapping.get(machine.id, 0)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'machine_id': machine.id,
                    'machine_name': machine.name,
                    'machine_model': machine.model,
                    'group_number': current_group_number,
                    'indicator_scores': indicator_scores,
                    'machine_group_mapping': machine_group_mapping,
                    'total_score': ensure_four_decimal_places(evaluation_result.total_score),
                    'machine': {
                        'id': machine.id,
                        'name': machine.name,
                        'model': machine.model,
                        'report_number': machine.report_number or f"RPT_{machine.id}",
                        'tolerance_group_1': machine.tolerance_group_1
                    }
                }
            })
            
        except Exception as e:
            print(f"获取用户评价结果时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_machine_tolerance_data(request):
    """API: 获取机床的允差数据 - 用于普通用户自动填充组别1"""
    if request.method == 'GET':
        try:
            from .models import Machine
            
            machine_id = request.GET.get('machine_id')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})
            
            # 获取机床对象
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': '机床不存在'})
            
            # 返回机床的允差数据
            return JsonResponse({
                'success': True,
                'machine': {
                    'id': machine.id,
                    'name': machine.name,
                    'model': machine.model,
                    'report_number': machine.report_number or f"RPT_{machine.id}",
                    'tolerance_group_1': machine.tolerance_group_1
                }
            })
            
        except Exception as e:
            print(f"获取机床允差数据时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_machine_group_mapping(request):
    """API: 获取机床与组别的映射关系"""
    if request.method == 'GET':
        try:
            from .models import Machine
            from django.db.models import Q
            
            # 获取机床类型参数，用于过滤
            machine_type = request.GET.get('machine_type', None)
            
            # 获取所有机床列表，建立机床与组别的映射关系
            # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床（admin_saved=True）
            # 普通用户只能看到自己创建的机床
            user_profile = request.user.userprofile
            if user_profile.is_admin():
                all_machines = Machine.objects.filter(
                    Q(created_by=request.user) | Q(admin_saved=True)
                ).distinct().order_by('id')
            else:
                all_machines = Machine.objects.filter(created_by=request.user).order_by('id')
            
            # 如果指定了机床类型，按类型过滤
            if machine_type:
                all_machines = all_machines.filter(machine_type=machine_type)
                print(f"按机床类型过滤: {machine_type}, 过滤后机床数量: {all_machines.count()}")
            
            machine_group_mapping = {}
            for index, m in enumerate(all_machines, start=1):
                machine_group_mapping[index] = m.id
            
            print(f"获取机床-组别映射关系: {machine_group_mapping}, 机床类型: {machine_type}")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'machine_group_mapping': machine_group_mapping,
                    'total_machines': all_machines.count()
                }
            })
            
        except Exception as e:
            print(f"获取机床-组别映射关系时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_tolerances_by_machine_data(request):
    """API: 根据机床数据获取允差"""
    if request.method == 'POST':
        try:
            import json
            from .models import Machine
            
            # 解析请求数据
            data = json.loads(request.body)
            
            # 获取机床参数
            machine_type = data.get('machine_type')
            x_axis_travel = data.get('x_axis_travel')
            y_axis_travel = data.get('y_axis_travel')
            z_axis_travel = data.get('z_axis_travel')
            worktable_length = data.get('worktable_length')
            workpiece_size = data.get('workpiece_size')
            spindle_type = data.get('spindle_type')
            
            # 验证必填参数
            if not machine_type:
                return JsonResponse({'success': False, 'error': '机床类型不能为空'})
            
            # 允差匹配/计算逻辑
            # 根据机床类型和参数匹配对应的允差值
            tolerance_group_1 = calculate_tolerances_for_group_1(
                machine_type, x_axis_travel, y_axis_travel, z_axis_travel,
                worktable_length, workpiece_size, spindle_type
            )
            
            # 如果提供了机床ID，则将允差值保存到数据库
            machine_id = data.get('machine_id')
            if machine_id:
                try:
                    machine = Machine.objects.get(id=machine_id)
                    machine.tolerance_group_1 = tolerance_group_1
                    machine.save()
                    print(f'允差值已保存到机床ID {machine_id} 的tolerance_group_1字段')
                except Machine.DoesNotExist:
                    print(f'机床ID {machine_id} 不存在，跳过允差值保存')
                except Exception as e:
                    print(f'保存允差值到数据库时出错: {e}')
            
            return JsonResponse({
                'success': True,
                'tolerance_group_1': tolerance_group_1
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def calculate_tolerances_for_group_1(machine_type, x_axis_travel, y_axis_travel, z_axis_travel,
                                   worktable_length, workpiece_size, spindle_type):
    """
    根据机床参数计算组别1的允差值
    根据X轴行程动态选择对应的允差值
    """
    
    # 根据X轴行程计算对应的允差值
    def get_tolerance_by_x_axis_travel(x_travel):
        if x_travel is None:
            return 0.020  # 默认值
        
        x_travel = float(x_travel)
        if x_travel <= 500:
            return 0.010
        elif 500 < x_travel <= 800:
            return 0.015
        elif 800 < x_travel <= 1250:
            return 0.020
        elif 1250 < x_travel <= 2000:
            return 0.025
        else:
            return 0.030  # 超出范围时的默认值
    
    # 获取X轴对应的允差值
    x_tolerance = get_tolerance_by_x_axis_travel(x_axis_travel)
    
    # 构建允差数据 - 使用动态计算的允差值
    tolerances = {
        '进给轴精度': {
            'X轴直线度': x_tolerance,
            'Y轴直线度': 0.010,  # 独立值
            'Z轴直线度': 0.010,  # 独立值
            '平行度': 0.010      # 独立值
        },
        '角度误差': {
            'X轴角度误差': 0.005,  # 独立值
            'Y轴角度误差': 0.005,  # 独立值
            'Z轴角度误差': 0.005   # 独立值
        },
        '垂直度': {
            'Y轴、X轴垂直度': 0.004,  # 独立值
            'Y轴、Z轴垂直度': 0.004,  # 独立值
            'Z轴、X轴垂直度': 0.004   # 独立值
        },
        '主轴垂直度': {
            '主轴轴线和X轴轴线运动间的垂直度': 0.002,  # 独立值
            '主轴轴线和Y轴轴线运动间的垂直度': 0.002   # 独立值
        }
    }
    
    return tolerances


def calculate_boring_milling_tolerances(column_measurement_range, x_axis_range=None, y_axis_range=None):
    """
    根据镗铣床立柱测量范围、X轴测量范围和Y轴测量范围计算几何精度允差值
    
    参数:
        column_measurement_range: 立柱测量范围(mm)
        x_axis_range: X轴测量范围(mm)，可选
        y_axis_range: Y轴测量范围(mm)，可选
    
    返回:
        dict: 包含所有项目的允差值
    """
    if column_measurement_range is None:
        column_measurement_range = 1000  # 默认值
    
    column_measurement_range = float(column_measurement_range)
    
    # 1. 立柱移动的直线度允差
    # ≤1000mm: 0.020, >1000mm: 0.030
    column_linearity_tolerance = 0.020 if column_measurement_range <= 1000 else 0.030
    
    # 2. 立柱移动的角度偏差允差
    # 固定值: 0.040
    column_angle_tolerance = 0.040
    
    # 3. 工作台面对立柱移动的平行度允差
    # 根据范围分段: ≤1000(0.030), 1000-3000(0.040), 3000-4000(0.050), >4000(0.060)
    if column_measurement_range <= 1000:
        table_column_parallelism = 0.030
    elif column_measurement_range <= 3000:
        table_column_parallelism = 0.040
    elif column_measurement_range <= 4000:
        table_column_parallelism = 0.050
    else:
        table_column_parallelism = 0.060
    
    tolerances = {
        '立柱相关': {
            '立柱移动的直线度': {
                'YZ垂直平面内(EYW)': column_linearity_tolerance,
                'ZX水平平面内(EXW)': column_linearity_tolerance,
                '立柱测量范围': column_measurement_range
            },
            '立柱移动的角度偏差': {
                'YZ平面内俯仰(EAW)': column_angle_tolerance,
                'XY平面内倾斜(ECW)': column_angle_tolerance,
                'ZX平面内偏摆(EBW)': column_angle_tolerance
            },
            '工作台面对立柱移动的平行度': {
                '允差值': table_column_parallelism,
                '立柱测量范围': column_measurement_range
            }
        }
    }
    
    # 如果提供了X轴测量范围，计算X轴相关允差
    if x_axis_range is not None:
        x_axis_range = float(x_axis_range)
        
        # 4. 工作台移动（X轴）的直线度允差
        # 根据范围分段: ≤1000(0.020), 1000-2000(0.030), 2000-3000(0.040), 3000-4000(0.050)
        if x_axis_range <= 1000:
            x_axis_linearity = 0.020
        elif x_axis_range <= 2000:
            x_axis_linearity = 0.030
        elif x_axis_range <= 3000:
            x_axis_linearity = 0.040
        else:
            x_axis_linearity = 0.050
        
        # 5. 工作台移动（X轴）的角度偏差允差
        # ≤4000mm: 0.040, >4000mm: 0.060
        x_axis_angle = 0.040 if x_axis_range <= 4000 else 0.060
        
        # 6. 工作台面对工作台移动（X轴）的平行度允差
        # 根据范围分段: ≤1000(0.030), 1000-3000(0.040), 3000-4000(0.050), 4000-5000(0.060)
        if x_axis_range <= 1000:
            table_x_axis_parallelism = 0.030
        elif x_axis_range <= 3000:
            table_x_axis_parallelism = 0.040
        elif x_axis_range <= 4000:
            table_x_axis_parallelism = 0.050
        else:
            table_x_axis_parallelism = 0.060
        
        tolerances['X轴相关'] = {
            '工作台移动（X轴）的直线度': {
                'XY垂直平面内(EYX)': x_axis_linearity,
                'ZX水平平面内(EZX)': x_axis_linearity,
                'X轴测量范围': x_axis_range
            },
            '工作台移动（X轴）的角度偏差': {
                'XY平面内俯仰(ECX)': x_axis_angle,
                'YZ平面内倾斜(EAX)': x_axis_angle,
                'ZX平面内偏摆(EBX)': x_axis_angle,
                'X轴测量范围': x_axis_range
            },
            '工作台面对工作台移动（X轴）的平行度': {
                '允差值': table_x_axis_parallelism,
                'X轴测量范围': x_axis_range
            }
        }
    
    # 如果提供了Y轴测量范围，计算Y轴相关允差
    if y_axis_range is not None:
        y_axis_range = float(y_axis_range)
        
        # 7. 主轴箱移动（Y轴）的直线度允差
        # 根据范围分段: ≤1000(0.020), 1000-2000(0.030), 2000-3000(0.040), 3000-4000(0.050)
        # 4000-5000(0.070), 5000-6000(0.090), 6000-7000(0.110)
        if y_axis_range <= 1000:
            y_axis_linearity = 0.020
        elif y_axis_range <= 2000:
            y_axis_linearity = 0.030
        elif y_axis_range <= 3000:
            y_axis_linearity = 0.040
        elif y_axis_range <= 4000:
            y_axis_linearity = 0.050
        elif y_axis_range <= 5000:
            y_axis_linearity = 0.070
        elif y_axis_range <= 6000:
            y_axis_linearity = 0.090
        else:
            y_axis_linearity = 0.110
        
        # 8. 主轴箱移动（Y轴）的角度偏差允差
        # ≤4000mm: 0.040, >4000mm: 0.060
        y_axis_angle = 0.040 if y_axis_range <= 4000 else 0.060
        
        tolerances['Y轴相关'] = {
            '主轴箱移动（Y轴）的直线度': {
                'YZ平面内(EZY)': y_axis_linearity,
                'XY平面内(EXY)': y_axis_linearity,
                'Y轴测量范围': y_axis_range
            },
            '主轴箱移动（Y轴）的角度偏差': {
                'YZ平面内俯仰(EAY)': y_axis_angle,
                'ZX平面内偏摆(EBY)': y_axis_angle,
                'Y轴测量范围': y_axis_range
            }
        }
    
    return tolerances


def get_boring_milling_tolerances(request):
    """API: 根据镗铣床立柱测量范围、X轴测量范围、Y轴测量范围、工作台长边长度、镗轴直径、铣轴直径和工作台类型获取几何精度允差"""
    if request.method == 'POST':
        try:
            import json
            from .models import Machine
            
            # 解析请求数据
            data = json.loads(request.body)
            
            # 获取立柱测量范围、X轴测量范围、Y轴测量范围、工作台长边长度、镗轴直径、铣轴直径和工作台类型
            column_measurement_range = data.get('column_measurement_range')
            x_axis_range = data.get('x_axis_range')
            y_axis_range = data.get('y_axis_range')
            worktable_length = data.get('worktable_length')
            boring_axis_diameter = data.get('boring_axis_diameter')
            milling_axis_diameter = data.get('milling_axis_diameter')
            worktable_type = data.get('worktable_type')  # 新增：工作台类型
            machine_id = data.get('machine_id')
            
            # 验证参数
            if column_measurement_range is None:
                return JsonResponse({'success': False, 'error': '立柱测量范围不能为空'})
            
            # 计算允差值（包含立柱相关、X轴相关、Y轴相关和工作台平面度）
            tolerances = calculate_boring_milling_tolerances(column_measurement_range, x_axis_range, y_axis_range)
            
            # 如果提供了工作台长边长度，计算工作台平面度允差
            if worktable_length is not None:
                worktable_length = float(worktable_length)
                
                # 9. 工作台面的平面度允差
                # 根据范围分段: ≤1000(0.030), 1000-3000(0.040), 3000-4000(0.050), 4000-5000(0.060)
                if worktable_length <= 1000:
                    flatness_tolerance = 0.030
                elif worktable_length <= 3000:
                    flatness_tolerance = 0.040
                elif worktable_length <= 4000:
                    flatness_tolerance = 0.050
                else:
                    flatness_tolerance = 0.060
                
                tolerances['工作台平面度'] = {
                    '允差值': flatness_tolerance,
                    '工作台长边长度': worktable_length
                }
            
            # 如果提供了镗轴直径，计算镗轴相关允差
            if boring_axis_diameter is not None:
                boring_axis_diameter = float(boring_axis_diameter)
                
                # 10. 镗轴直径相关允差
                # 当D≤125时: 镗轴锥孔径向跳动0.010、镗轴径向跳动0.010、轴向窜动0.010
                # 当D>125时: 镗轴锥孔径向跳动0.030、镗轴径向跳动0.030、轴向窜动0.015
                if boring_axis_diameter <= 125:
                    spindle_bore_runout = 0.010
                    spindle_runout = 0.010
                    axial_play = 0.010
                else:
                    spindle_bore_runout = 0.030
                    spindle_runout = 0.030
                    axial_play = 0.015
                
                tolerances['镗轴直径相关'] = {
                    '镗轴锥孔的径向跳动': {
                        '允差值': spindle_bore_runout,
                        '镗轴直径': boring_axis_diameter
                    },
                    '镗轴的径向跳动': {
                        '允差值': spindle_runout,
                        '镗轴直径': boring_axis_diameter
                    },
                    '周期性的轴向窜动': {
                        '允差值': axial_play,
                        '镗轴直径': boring_axis_diameter
                    }
                }
            
            # 如果提供了铣轴直径，计算铣轴相关允差
            if milling_axis_diameter is not None:
                milling_axis_diameter = float(milling_axis_diameter)
                
                # 11. 铣轴直径相关允差
                # 当D≤125时: 铣轴端部径向跳动0.010、铣轴端部轴向窜动0.010
                # 当D>125时: 铣轴端部径向跳动0.015、铣轴端部轴向窜动0.015
                if milling_axis_diameter <= 125:
                    milling_axis_runout = 0.010
                    milling_axis_axial_play = 0.010
                else:
                    milling_axis_runout = 0.015
                    milling_axis_axial_play = 0.015
                
                tolerances['铣轴直径相关'] = {
                    '铣轴端部的径向跳动': {
                        '允差值': milling_axis_runout,
                        '铣轴直径': milling_axis_diameter
                    },
                    '铣轴端部的周期性轴向窜动': {
                        '允差值': milling_axis_axial_play,
                        '铣轴直径': milling_axis_diameter
                    }
                }
            
            # 如果提供了工作台类型，计算位置精度允差
            if worktable_type:
                # 12. 工作台类型相关的位置精度允差
                # 固定分度: 双向定位精度11.000、单向重复定位精度6.000
                # 任意角度定位: 双向定位精度18.000、单向重复定位精度10.000
                if '任意角度' in worktable_type or '定位' in worktable_type:
                    positioning_accuracy = 18.000
                    repeatability = 10.000
                else:
                    # 默认固定分度
                    positioning_accuracy = 11.000
                    repeatability = 6.000
                
                tolerances['工作台类型相关'] = {
                    '双向定位精度': {
                        '允差值': positioning_accuracy,
                        '工作台类型': worktable_type
                    },
                    '单向重复定位精度': {
                        '允差值': repeatability,
                        '工作台类型': worktable_type
                    }
                }
            
            # 如果提供了机床ID，则将允差值保存到数据库
            if machine_id:
                try:
                    machine = Machine.objects.get(id=machine_id)
                    # 将镗铣床允差保存到 tolerance_group_1 字段（JSON格式）
                    existing_tolerances = machine.tolerance_group_1 or {}
                    existing_tolerances.update({
                        'boring_milling_geometric': tolerances
                    })
                    machine.tolerance_group_1 = existing_tolerances
                    machine.save()
                    print(f'镗铣床允差值已保存到机床ID {machine_id} 的tolerance_group_1字段')
                except Machine.DoesNotExist:
                    print(f'机床ID {machine_id} 不存在，跳过允差值保存')
                except Exception as e:
                    print(f'保存镗铣床允差值到数据库时出错: {e}')
            
            return JsonResponse({
                'success': True,
                'tolerances': tolerances,
                'column_measurement_range': column_measurement_range,
                'x_axis_range': x_axis_range,
                'y_axis_range': y_axis_range,
                'worktable_length': worktable_length,
                'boring_axis_diameter': boring_axis_diameter,
                'milling_axis_diameter': milling_axis_diameter,
                'worktable_type': worktable_type
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_measured_values(request):
    """API: 获取测量值"""
    if request.method == 'GET':
        try:
            from .models import Machine
            
            machine_id = request.GET.get('machine_id')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})
            
            # 尝试获取机床对象，如果不存在则使用默认配置
            machine = None
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                print(f"机床ID {machine_id} 不存在，使用默认权重配置")
            
            # 根据机床ID生成不同的测量值数据
            machine_measured_configs = {
                '1': {
                    '几何精度': {
                        '进给轴精度': [0.015, 0.018, 0.012, 0.3],
                        '工作台精度': [0.012, 0.016, 0.018],
                        '主轴精度': [0.003, 0.0015, 0.0018, 0.0025, 0.0012],
                        '刀库精度': [0.012, 0.006]
                    },
                    '位置精度': {
                        '重复定位精度': [0.006],
                        '定位精度': [0.010],
                        '平均位置偏移': [0.004],
                        '定位系统偏差': [0.005],
                        '最小分辨率': [0.0012],
                        '反向间隙(差值)': [0.0025]
                    },
                    '加工精度': {
                        '微观几何形状误差': [2.0],
                        '加工分散性': [1.15],
                        '工件几何精度': [0.012, 0.009]
                    },
                    '运动精度': {
                        '主轴运动精度': [0.0035, 0.0018, 0.3, 1.2, 0.6],
                        '多轴联动精度': [0.012, 0.022, 0.018, 0.022, 0.012],
                        '传动精度': [0.012, 0.018, 0.022, 0.012],
                        '热误差': [0.006, 0.004, 0.005],
                        '磨损精度': [0.12, 0.06]
                    }
                },
                '2': {
                    '几何精度': {
                        '进给轴精度': [0.012, 0.015, 0.010, 0.25],
                        '工作台精度': [0.010, 0.014, 0.016],
                        '主轴精度': [0.0025, 0.0012, 0.0015, 0.002, 0.001],
                        '刀库精度': [0.010, 0.005]
                    },
                    '位置精度': {
                        '重复定位精度': [0.005],
                        '定位精度': [0.008],
                        '平均位置偏移': [0.003],
                        '定位系统偏差': [0.004],
                        '最小分辨率': [0.001],
                        '反向间隙(差值)': [0.002]
                    },
                    '加工精度': {
                        '微观几何形状误差': [1.8],
                        '加工分散性': [1.1],
                        '工件几何精度': [0.010, 0.008]
                    },
                    '运动精度': {
                        '主轴运动精度': [0.003, 0.0015, 0.25, 1.0, 0.5],
                        '多轴联动精度': [0.010, 0.020, 0.016, 0.020, 0.010],
                        '传动精度': [0.010, 0.016, 0.020, 0.010],
                        '热误差': [0.005, 0.003, 0.004],
                        '磨损精度': [0.10, 0.05]
                    }
                },
                '3': {
                    '几何精度': {
                        '进给轴精度': [0.018, 0.021, 0.015, 0.35],
                        '工作台精度': [0.014, 0.018, 0.020],
                        '主轴精度': [0.0035, 0.0018, 0.0021, 0.003, 0.0015],
                        '刀库精度': [0.014, 0.007]
                    },
                    '位置精度': {
                        '重复定位精度': [0.007],
                        '定位精度': [0.012],
                        '平均位置偏移': [0.005],
                        '定位系统偏差': [0.006],
                        '最小分辨率': [0.0014],
                        '反向间隙(差值)': [0.003]
                    },
                    '加工精度': {
                        '微观几何形状误差': [2.2],
                        '加工分散性': [1.2],
                        '工件几何精度': [0.014, 0.010]
                    },
                    '运动精度': {
                        '主轴运动精度': [0.004, 0.002, 0.35, 1.4, 0.7],
                        '多轴联动精度': [0.014, 0.024, 0.020, 0.024, 0.014],
                        '传动精度': [0.014, 0.020, 0.024, 0.014],
                        '热误差': [0.007, 0.005, 0.006],
                        '磨损精度': [0.14, 0.07]
                    }
                },
                '4': {
                    '几何精度': {
                        '进给轴精度': [0.010, 0.013, 0.009, 0.2],
                        '工作台精度': [0.009, 0.013, 0.015],
                        '主轴精度': [0.002, 0.001, 0.0013, 0.0018, 0.0008],
                        '刀库精度': [0.009, 0.004]
                    },
                    '位置精度': {
                        '重复定位精度': [0.004],
                        '定位精度': [0.006],
                        '平均位置偏移': [0.002],
                        '定位系统偏差': [0.003],
                        '最小分辨率': [0.0008],
                        '反向间隙(差值)': [0.0015]
                    },
                    '加工精度': {
                        '微观几何形状误差': [1.5],
                        '加工分散性': [1.0],
                        '工件几何精度': [0.008, 0.006]
                    },
                    '运动精度': {
                        '主轴运动精度': [0.0025, 0.0012, 0.2, 0.8, 0.4],
                        '多轴联动精度': [0.008, 0.018, 0.014, 0.018, 0.008],
                        '传动精度': [0.008, 0.014, 0.018, 0.008],
                        '热误差': [0.004, 0.002, 0.003],
                        '磨损精度': [0.08, 0.04]
                    }
                }
            }
            
            # 获取当前机床的测量值配置，如果不存在则使用默认配置
            measured_values = machine_measured_configs.get(machine_id, machine_measured_configs['1'])
            
            return JsonResponse({'success': True, 'values': measured_values})
            
        except Machine.DoesNotExist:
            # 机床不存在时，使用默认标准值配置
            print(f"机床ID {machine_id} 不存在，使用默认标准值配置")
            # 默认标准值配置
            default_standards = {
                '几何精度': {
                    '进给轴精度': [0.01, 0.02, 0.01, 0.5],
                    '工作台精度': [0.01, 0.015, 0.02],
                    '主轴精度': [0.002, 0.001, 0.0015, 0.002, 0.001],
                    '刀库精度': [0.01, 0.005]
                },
                '位置精度': {
                    '重复定位精度': [0.005],
                    '定位精度': [0.008],
                    '平均位置偏移': [0.003],
                    '定位系统偏差': [0.004],
                    '最小分辨率': [0.001],
                    '反向间隙(差值)': [0.002]
                },
                '加工精度': {
                    '微观几何形状误差': [1.6],
                    '加工分散性': [1.0],
                    '工件几何精度': [0.01, 0.008]
                },
                '运动精度': {
                    '主轴运动精度': [0.002, 0.001, 0.5, 1.0, 0.6],
                    '多轴联动精度': [0.01, 0.02, 0.015, 0.02, 0.01],
                    '传动精度': [0.01, 0.015, 0.02, 0.01],
                    '热误差': [0.005, 0.003, 0.004],
                    '磨损精度': [0.1, 0.05]
                }
            }
            return JsonResponse({'success': True, 'values': default_standards})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_standard_values(request):
    """API: 获取标准值"""
    if request.method == 'GET':
        try:
            from .models import Machine, EntropyWeight
            
            machine_id = request.GET.get('machine_id')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})
            
            # 获取机床对象
            machine = Machine.objects.get(id=machine_id)
            
            # 从数据库获取该机床的标准值数据
            entropy_weights = EntropyWeight.objects.filter(
                machine__id=machine_id
            ).order_by('-calculated_at')
            
            # 初始化标准值字典
            standard_values = {
                '几何精度': {
                    '进给轴精度': [0.01, 0.02, 0.01, 0.5],
                    '工作台精度': [0.01, 0.015, 0.02],
                    '主轴精度': [0.002, 0.001, 0.0015, 0.002, 0.001],
                    '刀库精度': [0.01, 0.005]
                },
                '位置精度': {
                    '重复定位精度': [0.005],
                    '定位精度': [0.008],
                    '平均位置偏移': [0.003],
                    '定位系统偏差': [0.004],
                    '最小分辨率': [0.001],
                    '反向间隙(差值)': [0.002]
                },
                '加工精度': {
                    '微观几何形状误差': [1.6],
                    '加工分散性': [1.0],
                    '工件几何精度': [0.01, 0.008]
                },
                '运动精度': {
                    '主轴运动精度': [0.002, 0.001, 0.5, 1.0, 0.6],
                    '多轴联动精度': [0.01, 0.02, 0.015, 0.02, 0.01],
                    '传动精度': [0.01, 0.015, 0.02, 0.01],
                    '热误差': [0.005, 0.003, 0.004],
                    '磨损精度': [0.1, 0.05]
                }
            }
            
            # 遍历所有信息熵权重数据，根据描述字段匹配到对应的指标
            for ew in entropy_weights:
                if ew.standard_values:
                    description = ew.description
                    if '进给轴精度' in description:
                        standard_values['几何精度']['进给轴精度'] = ew.standard_values
                    elif '工作台精度' in description:
                        standard_values['几何精度']['工作台精度'] = ew.standard_values
                    elif '主轴精度' in description:
                        standard_values['几何精度']['主轴精度'] = ew.standard_values
                    elif '刀库精度' in description:
                        standard_values['几何精度']['刀库精度'] = ew.standard_values
                    elif '重复定位精度' in description:
                        standard_values['位置精度']['重复定位精度'] = ew.standard_values
                    elif '定位精度' in description and '平均位置偏移' not in description and '定位系统偏差' not in description:
                        standard_values['位置精度']['定位精度'] = ew.standard_values
                    elif '平均位置偏移' in description:
                        standard_values['位置精度']['平均位置偏移'] = ew.standard_values
                    elif '定位系统偏差' in description:
                        standard_values['位置精度']['定位系统偏差'] = ew.standard_values
                    elif '最小分辨率' in description:
                        standard_values['位置精度']['最小分辨率'] = ew.standard_values
                    elif '反向间隙' in description:
                        standard_values['位置精度']['反向间隙(差值)'] = ew.standard_values
                    elif '微观几何形状误差' in description:
                        standard_values['加工精度']['微观几何形状误差'] = ew.standard_values
                    elif '加工分散性' in description:
                        standard_values['加工精度']['加工分散性'] = ew.standard_values
                    elif '工件几何精度' in description:
                        standard_values['加工精度']['工件几何精度'] = ew.standard_values
                    elif '主轴运动精度' in description:
                        standard_values['运动精度']['主轴运动精度'] = ew.standard_values
                    elif '多轴联动精度' in description:
                        standard_values['运动精度']['多轴联动精度'] = ew.standard_values
                    elif '传动精度' in description:
                        standard_values['运动精度']['传动精度'] = ew.standard_values
                    elif '热误差' in description:
                        standard_values['运动精度']['热误差'] = ew.standard_values
                    elif '磨损精度' in description:
                        standard_values['运动精度']['磨损精度'] = ew.standard_values
            
            return JsonResponse({'success': True, 'values': standard_values})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def calculate_comprehensive_weight(request):
    """API: 计算综合权重"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ahp_weights = data.get('ahp_weights')
            entropy_weights = data.get('entropy_weights')
            alpha = data.get('alpha', 0.5)  # 默认值为0.5
            
            # 检查必要参数
            if not ahp_weights or not entropy_weights:
                return JsonResponse({'success': False, 'error': 'AHP权重和信息熵权重不能为空'})
            
            # 计算综合权重
            comprehensive_weights = {}
            for category, ahp_category_weights in ahp_weights.items():
                comprehensive_weights[category] = {}
                for subcategory, ahp_subcategory_weights in ahp_category_weights.items():
                    comprehensive_weights[category][subcategory] = {}
                    for indicator, ahp_weight in ahp_subcategory_weights.items():
                        entropy_weight = entropy_weights.get(category, {}).get(subcategory, {}).get(indicator, 0)
                        # 计算综合权重: α * AHP权重 + (1-α) * 信息熵权重
                        comprehensive_weight = alpha * ahp_weight + (1 - alpha) * entropy_weight
                        comprehensive_weights[category][subcategory][indicator] = comprehensive_weight
            
            return JsonResponse({
                'success': True,
                'comprehensive_weights': comprehensive_weights,
                'message': '综合权重计算成功'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_tolerances(request):
    """API: 获取允差"""
    if request.method == 'GET':
        try:
            from .models import Machine

            machine_id = request.GET.get('machine_id')

            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})

            # 获取机床对象
            machine = Machine.objects.get(id=machine_id)

            # 根据机床类型获取对应的允差配置
            machine_type = machine.machine_type
            
            # 加工中心允差配置
            machining_center_tolerances = {
                '几何精度': {
                    '进给轴精度': [0.02, 0.015, 0.015, 0.06],
                    '工作台精度': [0.025, 0.04, 0.03],
                    '主轴精度': [0, 0, 0.007, 0, 0.005],
                    '刀库精度': [0, 0]
                },
                '位置精度': {
                    '重复定位精度': [0.018],
                    '定位精度': [0.032],
                    '平均位置偏移': [0.02],
                    '定位系统偏差': [0.023],
                    '最小分辨率': [0],
                    '反向间隙(差值)': [0.012]
                },
                '加工精度': {
                    '微观几何形状误差': [0],
                    '加工分散性': [0],
                    '工件几何精度': [0.02, 0]
                },
                '运动精度': {
                    '主轴运动精度': [0, 0, 0, 0, 0],
                    '多轴联动精度': [0, 0, 0, 0, 0],
                    '传动精度': [0, 0, 0, 0],
                    '热误差': [0, 0, 0],
                    '磨损精度': [0, 0]
                }
            }
            
            # 镗铣床允差配置
            boring_milling_machine_tolerances = {
                '几何精度': {
                    '进给轴精度': [0.01, 0.01, 0.01, 0.01],
                    '工作台精度': [0.02, 0.025, 0.03],
                    '主轴精度': [0.015, 0.02, 0.007, 0.025, 0.005],
                    '刀库精度': [0.02, 0.01]
                },
                '位置精度': {
                    '重复定位精度': [0.01],
                    '定位精度': [0.015],
                    '平均位置偏移': [0.006],
                    '定位系统偏差': [0.008],
                    '最小分辨率': [0.002],
                    '反向间隙(差值)': [0.004]
                },
                '加工精度': {
                    '微观几何形状误差': [3.2],
                    '加工分散性': [0.3],
                    '工件几何精度': [0.02, 0.015]
                },
                '运动精度': {
                    '主轴运动精度': [0.005, 0.003, 1.0, 2.0, 1.0],
                    '多轴联动精度': [0.02, 0.03, 0.025, 0.03, 0.02],
                    '传动精度': [0.02, 0.025, 0.03, 0.02],
                    '热误差': [0.01, 0.006, 0.008],
                    '磨损精度': [0.2, 0.1]
                }
            }
            
            # 根据机床类型选择对应的允差配置
            if machine_type == 'machining_center':
                tolerances = machining_center_tolerances
            elif machine_type == 'boring_milling_machine':
                tolerances = boring_milling_machine_tolerances
            else:
                # 默认使用加工中心允差配置
                tolerances = machining_center_tolerances
            
            return JsonResponse({'success': True, 'values': tolerances})
            
        except Machine.DoesNotExist:
            # 机床不存在时，使用默认允差配置（加工中心）
            print(f"机床ID {machine_id} 不存在，使用默认允差配置")
            # 默认允差配置（加工中心）
            default_tolerances = {
                '几何精度': {
                    '进给轴精度': [0.02, 0.03, 0.02, 1.0],
                    '工作台精度': [0.02, 0.025, 0.03],
                    '主轴精度': [0.015, 0.02, 0.007, 0.025, 0.005],
                    '刀库精度': [0.02, 0.01]
                },
                '位置精度': {
                    '重复定位精度': [0.01],
                    '定位精度': [0.015],
                    '平均位置偏移': [0.006],
                    '定位系统偏差': [0.008],
                    '最小分辨率': [0.002],
                    '反向间隙(差值)': [0.004]
                },
                '加工精度': {
                    '微观几何形状误差': [3.2],
                    '加工分散性': [0.3],
                    '工件几何精度': [0.02, 0.015]
                },
                '运动精度': {
                    '主轴运动精度': [0.005, 0.003, 1.0, 2.0, 1.0],
                    '多轴联动精度': [0.02, 0.03, 0.025, 0.03, 0.02],
                    '传动精度': [0.02, 0.025, 0.03, 0.02],
                    '热误差': [0.01, 0.006, 0.008],
                    '磨损精度': [0.2, 0.1]
                }
            }
            return JsonResponse({'success': True, 'values': default_tolerances})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_all_tolerances_data(request):
    """API: 获取所有机床类型的允差数据 - 用于前端全局自动加载"""
    if request.method == 'GET':
        try:
            from .models import Machine

            saved_machining_center = {}
            saved_boring_milling = {}

            mc_machines = Machine.objects.filter(
                machine_type='machining_center', 
                tolerance_group_1__isnull=False
            ).exclude(tolerance_group_1={})
            
            if mc_machines.exists():
                latest_mc = mc_machines.order_by('-updated_at').first()
                if latest_mc and latest_mc.tolerance_group_1:
                    saved_data = latest_mc.tolerance_group_1
                    if isinstance(saved_data, dict):
                        for key, value in saved_data.items():
                            if key == 'machining_center_geometric':
                                if isinstance(value, dict):
                                    for sub_key, sub_value in value.items():
                                        if isinstance(sub_value, dict):
                                            for k, v in sub_value.items():
                                                saved_machining_center[k] = v
                                        else:
                                            saved_machining_center[sub_key] = sub_value
                            else:
                                saved_machining_center[key] = value

            bm_machines = Machine.objects.filter(
                machine_type='boring_milling_machine', 
                tolerance_group_1__isnull=False
            ).exclude(tolerance_group_1={})
            
            if bm_machines.exists():
                latest_bm = bm_machines.order_by('-updated_at').first()
                if latest_bm and latest_bm.tolerance_group_1:
                    saved_data = latest_bm.tolerance_group_1
                    if isinstance(saved_data, dict):
                        for key, value in saved_data.items():
                            if key == 'boring_milling_geometric':
                                if isinstance(value, dict):
                                    for sub_key, sub_value in value.items():
                                        if isinstance(sub_value, dict):
                                            for k, v in sub_value.items():
                                                saved_boring_milling[k] = v
                                        else:
                                            saved_boring_milling[sub_key] = sub_value
                            else:
                                saved_boring_milling[key] = value

            print(f"[get_all_tolerances_data] 加工中心已保存数据条目数: {len(saved_machining_center)}")
            print(f"[get_all_tolerances_data] 镗铣床已保存数据条目数: {len(saved_boring_milling)}")

            result = {
                'machining_center': saved_machining_center,
                'boring_milling_machine': saved_boring_milling
            }

            return JsonResponse({'success': True, 'data': result})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_entropy_weights(request):
    """API: 获取信息熵权重"""
    if request.method == 'GET':
        try:
            from django.db import connection
            from .models import Machine
            import json
            
            machine_id = request.GET.get('machine_id')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})
            
            # 获取机床类型
            try:
                machine = Machine.objects.get(id=machine_id)
                machine_type = machine.machine_type
                print(f"[get_entropy_weights] 机床ID: {machine_id}, 机床类型: {machine_type}")
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': '机床不存在'})
            
            # 根据机床类型初始化权重结构
            # 加工中心: 工作台精度 = [平面度, 直线度, T型槽平行度]
            # 镗铣床: 工作台精度 = [平面度, 平行度, T型槽平行度]
            if machine_type == 'boring_milling_machine':
                weights = {
                    '几何精度': {
                        '进给轴精度': [0.0, 0.0, 0.0, 0.0],
                        '工作台精度': [0.0, 0.0, 0.0],  # 平面度, 平行度, T型槽平行度
                        '主轴精度': [0.0, 0.0, 0.0, 0.0, 0.0],
                        '刀库精度': [0.0, 0.0]
                    },
                    '位置精度': {
                        '重复定位精度': [0.0],
                        '定位精度': [0.0],
                        '平均位置偏移': [0.0],
                        '定位系统偏差': [0.0],
                        '最小分辨率': [0.0],
                        '反向间隙(差值)': [0.0]
                    },
                    '加工精度': {
                        '微观几何形状误差': [0.0],
                        '加工分散性': [0.0],
                        '工件几何精度': [0.0, 0.0]
                    },
                    '运动精度': {
                        '主轴运动精度': [0.0, 0.0, 0.0, 0.0, 0.0],
                        '多轴联动精度': [0.0, 0.0, 0.0, 0.0, 0.0],
                        '传动精度': [0.0, 0.0, 0.0, 0.0],
                        '热误差': [0.0, 0.0, 0.0],
                        '磨损精度': [0.0, 0.0]
                    }
                }
            else:
                # 加工中心默认结构
                weights = {
                    '几何精度': {
                        '进给轴精度': [0.0, 0.0, 0.0, 0.0],
                        '工作台精度': [0.0, 0.0, 0.0],  # 平面度, 直线度, T型槽平行度
                        '主轴精度': [0.0, 0.0, 0.0, 0.0, 0.0],
                        '刀库精度': [0.0, 0.0]
                    },
                    '位置精度': {
                        '重复定位精度': [0.0],
                        '定位精度': [0.0],
                        '平均位置偏移': [0.0],
                        '定位系统偏差': [0.0],
                        '最小分辨率': [0.0],
                        '反向间隙(差值)': [0.0]
                    },
                    '加工精度': {
                        '微观几何形状误差': [0.0],
                        '加工分散性': [0.0],
                        '工件几何精度': [0.0, 0.0]
                    },
                    '运动精度': {
                        '主轴运动精度': [0.0, 0.0, 0.0, 0.0, 0.0],
                        '多轴联动精度': [0.0, 0.0, 0.0, 0.0, 0.0],
                        '传动精度': [0.0, 0.0, 0.0, 0.0],
                        '热误差': [0.0, 0.0, 0.0],
                        '磨损精度': [0.0, 0.0]
                    }
                }
            
            # 定义精度类型到前端指标的映射
            precision_type_mapping = {
                'feed_axis': ('几何精度', '进给轴精度'),
                'worktable': ('几何精度', '工作台精度'),
                'spindle': ('几何精度', '主轴精度'),
                'tool_magazine': ('几何精度', '刀库精度'),
                'position': ('位置精度', None),
                'workpiece_geometry': ('加工精度', '工件几何精度'),
                'spindle_motion': ('运动精度', '主轴运动精度'),
                'multi_axis': ('运动精度', '多轴联动精度'),
                'transmission': ('运动精度', '传动精度'),
                'thermal_error': ('运动精度', '热误差'),
                'wear': ('运动精度', '磨损精度')
            }
            
            # 从ENTROPY_WEIGHT_DAMENG表获取数据，根据机床类型过滤
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT PRECISION_TYPE, INDICATOR_NAMES, WEIGHTS, MACHINE_TYPE
                    FROM ENTROPY_WEIGHT_DAMENG
                    WHERE MACHINE_TYPE = %s OR MACHINE_TYPE IS NULL
                    ORDER BY CALCULATED_AT DESC
                """, [machine_type])
                
                rows = cursor.fetchall()
                print(f"从ENTROPY_WEIGHT_DAMENG表获取到{len(rows)}条记录，机床类型过滤: {machine_type}")
                
                for row in rows:
                    precision_type = row[0]
                    indicator_names_str = row[1]
                    weights_str = row[2]
                    db_machine_type = row[3]
                    print(f"  处理记录: {precision_type}, 机床类型: {db_machine_type}")
                    
                    try:
                        indicator_names = json.loads(indicator_names_str) if indicator_names_str else []
                        weight_values = json.loads(weights_str) if weights_str else []
                    except:
                        print(f"  解析JSON失败: {precision_type}")
                        continue
                    
                    print(f"  PRECISION_TYPE: {precision_type}")
                    print(f"  INDICATOR_NAMES: {indicator_names}")
                    print(f"  WEIGHTS: {weight_values}")
                    
                    if precision_type in precision_type_mapping:
                        category, subcategory = precision_type_mapping[precision_type]
                        
                        if subcategory:
                            weights[category][subcategory] = weight_values
                            print(f"  -> 匹配到 {category}/{subcategory}")
                        elif precision_type == 'position':
                            if len(weight_values) >= 6:
                                weights['位置精度']['重复定位精度'] = [weight_values[0]]
                                weights['位置精度']['定位精度'] = [weight_values[1]]
                                weights['位置精度']['平均位置偏移'] = [weight_values[2]]
                                weights['位置精度']['定位系统偏差'] = [weight_values[3]]
                                weights['位置精度']['最小分辨率'] = [weight_values[4]]
                                weights['位置精度']['反向间隙(差值)'] = [weight_values[5]]
                                print(f"  -> 匹配到位置精度，权重分配完成")
            
            print(f"最终权重: {weights}")
            
            return JsonResponse({'success': True, 'weights': weights})
            
        except Exception as e:
            print(f"获取信息熵权重出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
def save_user_evaluation_result(request):
    """API: 保存用户评价结果 - 包含指标得分最低值及相关数据"""
    if request.method == 'POST':
        try:
            from .models import UserEvaluationResult, Machine
            
            data = json.loads(request.body)
            machine_id = data.get('machine_id')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})
            
            # 获取机床对象
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': '机床不存在'})
            
            # 检查是否已经存在该machine_id的记录
            existing_result = UserEvaluationResult.objects.filter(machine=machine).first()
            
            # 定义所有可更新的字段及其默认值
            all_fields = {
                'feed_axis_accuracy': None,
                'feed_axis_straightness_min_score': 0,
                'feed_axis_parallelism_min_score': 0,
                'feed_axis_angle_min_score': 0,
                'feed_axis_perpendicularity_min_score': 0,
                'worktable_accuracy': None,
                'worktable_flatness_min_score': 0,
                'worktable_tslot_min_score': 0,
                'worktable_straightness_min_score': 0,
                'worktable_parallelism_min_score': 0,
                'spindle_accuracy': None,
                'spindle_radial_min_score': 0,
                'spindle_axial_min_score': 0,
                'spindle_face_min_score': 0,
                'roundness': None,
                'coaxiality': None,
                'spindle_radial_runout': None,
                'spindle_end_runout': None,
                'spindle_axial_runout': None,
                'roundness_min_score': 0,
                'coaxiality_min_score': 0,
                'spindle_radial_runout_min_score': 0,
                'spindle_end_runout_min_score': 0,
                'spindle_axial_runout_min_score': 0,
                'tool_magazine_accuracy': None,
                'tool_magazine_positioning_min_score': 0,
                'tool_magazine_repeatability_min_score': 0,
                'position_accuracy': None,
                'position_repeatability_min_score': 0,
                'position_positioning_min_score': 0,
                'position_offset_min_score': 0,
                'position_deviation_min_score': 0,
                'position_resolution_min_score': 0,
                'position_backlash_min_score': 0,
                'machining_accuracy': None,
                'machining_surface_roughness_min_score': 0,
                'machining_process_capability_min_score': 0,
                'machining_dimension_min_score': 0,
                'machining_geometry_min_score': 0,
                'motion_accuracy': None,
                'motion_spindle_min_score': 0,
                'motion_multi_axis_min_score': 0,
                'motion_transmission_min_score': 0,
                'motion_thermal_min_score': 0,
                'motion_wear_min_score': 0,
                'motion_flatness_min_score': 0,
                'motion_profile_min_score': 0,
                'motion_space_min_score': 0,
                'motion_rtcp_min_score': 0,
                'motion_line_min_score': 0,
                'motion_servo_min_score': 0,
                'motion_overshoot_min_score': 0,
                'motion_crawl_min_score': 0,
                'motion_tool_wear_min_score': 0,
                'motion_grinding_wear_min_score': 0,
                'motion_angle_min_score': 0,
                'motion_start_stop_min_score': 0,
                'motion_balance_min_score': 0,
                'tolerance_data': None,
                'entropy_weights': None,
                'standard_values': None,
                'total_score': 0
            }
            
            # 如果存在记录则更新，否则创建新记录
            if existing_result:
                # 更新时只更新前端实际传递的字段
                updated_fields = []
                for field_name in all_fields.keys():
                    if field_name in data:
                        setattr(existing_result, field_name, data[field_name])
                        updated_fields.append(field_name)
                existing_result.save()
                result = existing_result
                print(f"更新机床ID {machine_id} 的用户评价结果，更新字段: {updated_fields}")
            else:
                # 创建新记录时使用前端传递的值或默认值
                evaluation_data = {
                    'machine': machine,
                    'evaluator': request.user,
                }
                for field_name, default_value in all_fields.items():
                    evaluation_data[field_name] = data.get(field_name, default_value)
                result = UserEvaluationResult.objects.create(**evaluation_data)
                print(f"创建机床ID {machine_id} 的用户评价结果")
            
            return JsonResponse({
                'success': True,
                'message': '用户评价结果保存成功',
                'result_id': result.id
            })
        except Exception as e:
            print(f"保存用户评价结果时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def calculate_entropy_weight_api(request):
    """API: 使用 Python 的 entropy.py 计算信息熵权重"""
    if request.method == 'POST':
        try:
            from .algorithms.entropy import calculate_entropy_weight
            import json
            
            data = json.loads(request.body)
            matrix_data = data.get('matrix_data', [])
            
            if not matrix_data or len(matrix_data) == 0:
                return JsonResponse({'success': False, 'error': '数据矩阵不能为空'})
            
            # 调用 entropy.py 中的 calculate_entropy_weight 函数
            result = calculate_entropy_weight(matrix_data)
            
            return JsonResponse({
                'success': True,
                'entropy': result['entropy'],
                'weights': result['weights']
            })
            
        except Exception as e:
            print(f"计算信息熵权重出错：{str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def save_entropy_result(request):
    """API: 保存信息熵权重计算结果"""
    if request.method == 'POST':
        try:
            from .models import EntropyWeight, Machine, DataOperationLog
            import json
            from django.db import transaction
            from datetime import datetime
            
            data = json.loads(request.body)
            machine_id = data.get('machine_id')
            precision_type = data.get('precision_type')
            
            if not precision_type:
                return JsonResponse({'success': False, 'error': '精度数据类型不能为空'})
            
            machine = None
            if machine_id:
                try:
                    machine_id = int(machine_id)
                    machine = Machine.objects.get(id=machine_id)
                except (ValueError, Machine.DoesNotExist):
                    machine = None
            
            def generate_total_id(precision_type, machine_id=None):
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                if machine_id:
                    return f"ENTROPY_{machine_id}_{precision_type}_{timestamp}"
                else:
                    return f"ENTROPY_{precision_type}_{timestamp}"
            
            total_id = generate_total_id(precision_type, machine_id)
            
            sample_count = data.get('sample_count', 0)
            description = data.get('description', '')
            results = data.get('results', [])
            input_data = data.get('input_data', [])
            
            indicator_names = []
            entropy_values = []
            weights = []
            
            for result in results:
                indicator_names.append(result.get('indicator_name', ''))
                entropy_values.append(float(result.get('entropy_value', '0')))
                weights.append(float(result.get('weight_value', '0')))
            
            tolerance_values = None
            if input_data and len(input_data) > 0:
                first_item = input_data[0]
                tolerance_values = first_item.get('tolerance_data', None)
            
            standard_values = data.get('standard_values', None)
            
            if machine:
                save_data = {
                    'evaluator': request.user,
                    'machine': machine,
                    'precision_type': precision_type,
                    'sample_count': sample_count,
                    'indicator_names': indicator_names,
                    'input_data': input_data,
                    'entropy_values': entropy_values,
                    'weights': weights,
                    'tolerance_values': tolerance_values,
                    'standard_values': standard_values,
                    'description': description,
                    'total_id': total_id
                }
                
                with transaction.atomic():
                    existing_record = EntropyWeight.objects.filter(machine=machine, precision_type=precision_type).first()
                    
                    if existing_record:
                        existing_record.total_id = total_id
                        existing_record.sample_count = sample_count
                        existing_record.indicator_names = indicator_names
                        existing_record.input_data = input_data
                        existing_record.entropy_values = entropy_values
                        existing_record.weights = weights
                        existing_record.tolerance_values = tolerance_values
                        existing_record.standard_values = standard_values
                        existing_record.description = description
                        existing_record.version += 1
                        existing_record.save()
                        
                        entropy_weight = existing_record
                    else:
                        entropy_weight = EntropyWeight.objects.create(**save_data)
            else:
                entropy_weight = None
            
            return JsonResponse({
                'success': True,
                'message': '计算结果保存成功',
                'calculation_id': entropy_weight.id if entropy_weight else None,
                'total_id': total_id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_machine_name(request):
    """API: 根据机床ID获取机床名称"""
    if request.method == 'GET':
        from .models import Machine
        from django.http import JsonResponse
        
        machine_id = request.GET.get('machine_id')
        
        if not machine_id:
            return JsonResponse({'success': False, 'error': '机床ID不能为空'})
        
        try:
            machine_id = int(machine_id)
        except ValueError:
            return JsonResponse({'success': False, 'error': '机床ID必须是整数'})
        
        try:
            machine = Machine.objects.get(id=machine_id)
            return JsonResponse({'success': True, 'machine_name': machine.name})
        except Machine.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def export_entropy_data(request):
    """API: 导出信息熵权重数据"""
    try:
        from .models import EntropyWeight, Machine
        import json
        from django.http import HttpResponse
        
        machine_id = request.GET.get('machine_id')
        
        if not machine_id:
            return JsonResponse({'success': False, 'error': '机床ID不能为空'})
        
        try:
            machine_id = int(machine_id)
        except ValueError:
            return JsonResponse({'success': False, 'error': '机床ID必须是整数'})
        
        # 获取机床对象
        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
        
        # 获取数据
        entropy_record = EntropyWeight.objects.filter(machine=machine).first()
        
        if not entropy_record:
            return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 没有关联的信息熵数据'})
        
        # 构建导出数据
        export_data = {
            'total_id': entropy_record.total_id,
            'machine_id': machine.id,
            'machine_name': machine.name,
            'evaluator': entropy_record.evaluator.username,
            'sample_count': entropy_record.sample_count,
            'indicator_names': entropy_record.indicator_names,
            'input_data': entropy_record.input_data,
            'entropy_values': entropy_record.entropy_values,
            'weights': entropy_record.weights,
            'tolerance_values': entropy_record.tolerance_values,
            'standard_values': entropy_record.standard_values,
            'description': entropy_record.description,
            'calculated_at': entropy_record.calculated_at.isoformat(),
            'updated_at': entropy_record.updated_at.isoformat(),
            'version': entropy_record.version
        }
        
        # 生成文件名
        filename = f"entropy_data_machine_{machine_id}_{entropy_record.total_id}.json"
        
        # 创建响应
        response = HttpResponse(
            json.dumps(export_data, ensure_ascii=False, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_all_machines(request):
    """API: 获取所有机床数据（支持按机床类型过滤）"""
    if request.method == 'GET':
        try:
            from .models import Machine
            from apps.data_management.services.dameng_service import DamengDatabaseService
            
            # 获取请求参数中的机床类型，默认为加工中心
            machine_type = request.GET.get('machine_type', 'machining_center')
            
            # 根据用户角色和机床类型过滤机床
            user_profile = request.user.userprofile
            if user_profile.is_admin():
                # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床
                machines = Machine.objects.filter(
                    Q(created_by=request.user) | Q(admin_saved=True),
                    machine_type=machine_type
                ).distinct().order_by('id')
            else:
                # 普通用户只能看到自己创建的机床
                machines = Machine.objects.filter(
                    created_by=request.user,
                    machine_type=machine_type
                ).order_by('id')
            
            # 从达梦数据库获取机床参数
            dameng_result = DamengDatabaseService.get_all_machines()
            dameng_machines = {}
            if dameng_result.get('success'):
                for dm_machine in dameng_result.get('data', []):
                    dameng_machines[dm_machine['machine_id']] = dm_machine
            
            # 从达梦数据库获取镗铣床参数
            from apps.data_management.services.boring_milling_service import BoringMillingService
            bm_result = BoringMillingService.get_all_boring_milling_machines()
            bm_machines = {}
            if bm_result.get('success'):
                for bm_machine in bm_result.get('data', []):
                    bm_machines[bm_machine['machine_id']] = bm_machine
            
            # 构建机床数据列表
            machine_list = []
            for machine in machines:
                # 从达梦数据库获取机床参数数据
                dm_data = dameng_machines.get(machine.id, {})
                # 镗铣床从专用表获取参数
                if machine.machine_type == 'boring_milling_machine':
                    bm_data = bm_machines.get(machine.id, {})
                    if bm_data:
                        dm_data = {**dm_data, **bm_data}  # 合并，镗铣床数据覆盖
                
                machine_data = {
                    'id': machine.id,
                    'name': machine.name,
                    'model': machine.model,
                    'machine_type': machine.machine_type,
                    'machine_type_display': dict(Machine.MACHINE_TYPES).get(machine.machine_type, machine.machine_type),
                    # 优先使用达梦数据库的xyz轴行程数据
                    'x_axis_travel': dm_data.get('x_axis_travel') if dm_data.get('x_axis_travel') else machine.x_axis_travel,
                    'y_axis_travel': dm_data.get('y_axis_travel') if dm_data.get('y_axis_travel') else machine.y_axis_travel,
                    'z_axis_travel': dm_data.get('z_axis_travel') if dm_data.get('z_axis_travel') else machine.z_axis_travel,
                    'worktable_length': machine.worktable_length,
                    'worktable_length_lc': dm_data.get('worktable_length_lc') if dm_data.get('worktable_length_lc') else machine.worktable_length_lc,
                    'workpiece_size': machine.workpiece_size,
                    'spindle_type': machine.spindle_type,
                    # 镗铣床特有参数 - 优先使用达梦数据库数据
                    'column_measurement_range': dm_data.get('column_measurement_range') if dm_data.get('column_measurement_range') else machine.column_measurement_range,
                    'worktable_x_range': dm_data.get('worktable_x_range') if dm_data.get('worktable_x_range') else machine.worktable_x_range,
                    'spindle_box_y_range': dm_data.get('spindle_box_y_range') if dm_data.get('spindle_box_y_range') else machine.spindle_box_y_range,
                    'z_axis_measurement_range': dm_data.get('z_axis_measurement_range') if dm_data.get('z_axis_measurement_range') else machine.z_axis_measurement_range,
                    'boring_axis_diameter': dm_data.get('boring_axis_diameter') if dm_data.get('boring_axis_diameter') else machine.boring_axis_diameter,
                    'milling_axis_diameter': dm_data.get('milling_axis_diameter') if dm_data.get('milling_axis_diameter') else machine.milling_axis_diameter,
                    'worktable_type': dm_data.get('worktable_type') if dm_data.get('worktable_type') else machine.worktable_type,
                }
                machine_list.append(machine_data)
            
            machine_type_display = dict(Machine.MACHINE_TYPES).get(machine_type, machine_type)
            print(f'DEBUG: 获取到 {len(machine_list)} 台{machine_type_display}')
            for m in machine_list:
                print(f'  - 机床 ID={m["id"]}, 名称={m["name"]}, 类型={m["machine_type"]}')
                if machine_type == 'boring_milling_machine':
                    print(f'    立柱测量范围={m.get("column_measurement_range")}, 工作台X轴={m.get("worktable_x_range")}, 主轴箱Y轴={m.get("spindle_box_y_range")}, Z轴测量范围={m.get("z_axis_measurement_range")}')
                    print(f'    工作台长度(Lc)={m.get("worktable_length_lc")}, 镗轴直径={m.get("boring_axis_diameter")}, 铣轴直径={m.get("milling_axis_diameter")}')
                else:
                    print(f'    X轴行程={m["x_axis_travel"]}, Y轴行程={m["y_axis_travel"]}, Z轴行程={m["z_axis_travel"]}')
            
            return JsonResponse({
                'success': True,
                'machines': machine_list,
                'count': len(machine_list),
                'machine_type': machine_type
            })
        except Exception as e:
            print(f'ERROR: 获取机床数据失败：{str(e)}')
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'获取机床数据失败：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_machining_center_linearity_data(request):
    """API: 获取加工中心直线度数据"""
    if request.method == 'GET':
        from apps.data_management.services.dameng_service import DamengDatabaseService
        
        try:
            # 从达梦数据库获取所有机床参数
            machines_result = DamengDatabaseService.get_all_machines()
            
            if not machines_result['success']:
                return JsonResponse({
                    'success': False,
                    'error': machines_result.get('error', '获取机床数据失败')
                })
            
            # 过滤出加工中心类型的数据
            horizontal_machines = []
            for machine in machines_result['data']:
                if machine.get('machine_type') == 'machining_center':
                    # 获取该机床的详细参数（包含直线度字段）
                    params_result = DamengDatabaseService.get_machine_parameters(machine['machine_id'])
                    if params_result['success']:
                        params = params_result['data']
                        horizontal_machines.append({
                            'machine_id': machine['machine_id'],
                            'machine_type': machine['machine_type'],
                            'x_axis_linearity_xy': params.get('x_axis_linearity_xy'),
                            'x_axis_linearity_zx': params.get('x_axis_linearity_zx'),
                            'z_axis_linearity_yz': params.get('z_axis_linearity_yz'),
                            'z_axis_linearity_zx': params.get('z_axis_linearity_zx'),
                            'y_axis_linearity_xy': params.get('y_axis_linearity_xy'),
                            'y_axis_linearity_yz': params.get('y_axis_linearity_yz'),
                            'spindle_parallelism_yz': params.get('spindle_parallelism_yz'),
                            'spindle_parallelism_zx': params.get('spindle_parallelism_zx'),
                            'x_axis_angle_pitch': params.get('x_axis_angle_pitch'),
                            'x_axis_angle_yaw': params.get('x_axis_angle_yaw'),
                            'x_axis_angle_roll': params.get('x_axis_angle_roll'),
                            'z_axis_angle_pitch': params.get('z_axis_angle_pitch'),
                            'z_axis_angle_yaw': params.get('z_axis_angle_yaw'),
                            'z_axis_angle_roll': params.get('z_axis_angle_roll'),
                            'y_axis_angle_xy': params.get('y_axis_angle_xy'),
                            'y_axis_angle_yz': params.get('y_axis_angle_yz'),
                            'y_axis_angle_zx': params.get('y_axis_angle_zx'),
                            'y_axis_perpendicularity_x': params.get('y_axis_perpendicularity_x'),
                            'y_axis_perpendicularity_z': params.get('y_axis_perpendicularity_z'),
                            'z_axis_perpendicularity_x': params.get('z_axis_perpendicularity_x'),
                            'spindle_perpendicularity_x': params.get('spindle_perpendicularity_x'),
                            'spindle_perpendicularity_y': params.get('spindle_perpendicularity_y'),
                            'worktable_flatness': params.get('worktable_flatness'),
                            'worktable_parallelism_x': params.get('worktable_parallelism_x'),
                            'worktable_parallelism_z': params.get('worktable_parallelism_z'),
                            'spindle_axial_runout': params.get('spindle_axial_runout'),
                            'spindle_radial_runout_near': params.get('spindle_radial_runout_near'),
                            'spindle_radial_runout_300mm': params.get('spindle_radial_runout_300mm'),
                            'linear_axis_repeatability_x': params.get('linear_axis_repeatability_x'),
                            'linear_axis_repeatability_y': params.get('linear_axis_repeatability_y'),
                            'linear_axis_repeatability_z': params.get('linear_axis_repeatability_z'),
                            'linear_axis_positioning_accuracy_x': params.get('linear_axis_positioning_accuracy_x'),
                            'linear_axis_positioning_accuracy_y': params.get('linear_axis_positioning_accuracy_y'),
                            'linear_axis_positioning_accuracy_z': params.get('linear_axis_positioning_accuracy_z'),
                            'linear_axis_mean_deviation_x': params.get('linear_axis_mean_deviation_x'),
                            'linear_axis_mean_deviation_y': params.get('linear_axis_mean_deviation_y'),
                            'linear_axis_mean_deviation_z': params.get('linear_axis_mean_deviation_z'),
                            'linear_axis_system_deviation_x': params.get('linear_axis_system_deviation_x'),
                            'linear_axis_system_deviation_y': params.get('linear_axis_system_deviation_y'),
                            'linear_axis_system_deviation_z': params.get('linear_axis_system_deviation_z'),
                            'linear_axis_backlash_x': params.get('linear_axis_backlash_x'),
                            'linear_axis_backlash_y': params.get('linear_axis_backlash_y'),
                            'linear_axis_backlash_z': params.get('linear_axis_backlash_z'),
                            'rotary_axis_repeatability_a': params.get('rotary_axis_repeatability_a'),
                            'rotary_axis_repeatability_b': params.get('rotary_axis_repeatability_b'),
                            'rotary_axis_repeatability_c': params.get('rotary_axis_repeatability_c'),
                            'rotary_axis_positioning_accuracy_a': params.get('rotary_axis_positioning_accuracy_a'),
                            'rotary_axis_positioning_accuracy_b': params.get('rotary_axis_positioning_accuracy_b'),
                            'rotary_axis_positioning_accuracy_c': params.get('rotary_axis_positioning_accuracy_c'),
                            'rotary_axis_mean_deviation_a': params.get('rotary_axis_mean_deviation_a'),
                            'rotary_axis_mean_deviation_b': params.get('rotary_axis_mean_deviation_b'),
                            'rotary_axis_mean_deviation_c': params.get('rotary_axis_mean_deviation_c'),
                            'rotary_axis_system_deviation_a': params.get('rotary_axis_system_deviation_a'),
                            'rotary_axis_system_deviation_b': params.get('rotary_axis_system_deviation_b'),
                            'rotary_axis_system_deviation_c': params.get('rotary_axis_system_deviation_c'),
                            'rotary_axis_backlash_a': params.get('rotary_axis_backlash_a'),
                            'rotary_axis_backlash_b': params.get('rotary_axis_backlash_b'),
                            'rotary_axis_backlash_c': params.get('rotary_axis_backlash_c'),
                            'cylindricity': params.get('cylindricity'),
                            'hole_perpendicularity_a': params.get('hole_perpendicularity_a'),
                            'side_linearity': params.get('side_linearity'),
                            'adjacent_perpendicularity_b': params.get('adjacent_perpendicularity_b'),
                            'opposite_parallelism_b': params.get('opposite_parallelism_b'),
                            'side_linearity_2': params.get('side_linearity_2'),
                            'side_inclination_b': params.get('side_inclination_b'),
                            'circularity': params.get('circularity'),
                            'concentricity_c': params.get('concentricity_c'),
                            'slope_linearity': params.get('slope_linearity'),
                            'slope_inclination_b': params.get('slope_inclination_b'),
                            'hole_position_c': params.get('hole_position_c'),
                            'concentricity_d': params.get('concentricity_d')
                        })
            
            return JsonResponse({
                'success': True,
                'machines': horizontal_machines,
                'count': len(horizontal_machines)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'获取加工中心直线度数据失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_boring_milling_machine_linearity_data(request):
    """API: 获取镗铣床直线度数据 - 使用独立镗铣床数据表"""
    if request.method == 'GET':
        from apps.data_management.services.boring_milling_service import BoringMillingService
        
        try:
            machines_result = BoringMillingService.get_all_boring_milling_machines()
            
            if not machines_result['success']:
                return JsonResponse({
                    'success': False,
                    'error': machines_result.get('message', '获取镗铣床数据失败')
                })
            
            boring_milling_machines = []
            for machine in machines_result['data']:
                params = machine
                boring_milling_machines.append({
                    'machine_id': params['machine_id'],
                    'machine_type': 'boring_milling_machine',
                    'column_linearity_yz': params.get('bm_column_linearity_yz'),
                    'column_linearity_zx': params.get('bm_column_linearity_zx'),
                    'worktable_x_linearity_xy': params.get('bm_worktable_x_linearity_xy'),
                    'worktable_x_linearity_zx': params.get('bm_worktable_x_linearity_zx'),
                    'spindle_box_y_linearity_yz': params.get('bm_spindle_box_y_linearity_yz'),
                    'spindle_box_y_linearity_xy': params.get('bm_spindle_box_y_linearity_xy'),
                    'column_angle_yz': params.get('bm_column_angle_yz'),
                    'column_angle_zx': params.get('bm_column_angle_zx'),
                    'column_angle_xy': params.get('bm_column_angle_xy'),
                    'worktable_x_angle_xy': params.get('bm_worktable_x_angle_xy'),
                    'worktable_x_angle_zx': params.get('bm_worktable_x_angle_zx'),
                    'worktable_x_angle_yz': params.get('bm_worktable_x_angle_yz'),
                    'spindle_box_y_angle_yz': params.get('bm_spindle_box_y_angle_yz'),
                    'spindle_box_y_angle_zx': params.get('bm_spindle_box_y_angle_zx'),
                    'worktable_x_column_perpendicularity': params.get('bm_worktable_x_column_perpendicularity'),
                    'spindle_box_y_worktable_x_perpendicularity': params.get('bm_spindle_box_y_worktable_x_perpendicularity'),
                    'spindle_box_y_column_perpendicularity': params.get('bm_spindle_box_y_column_perpendicularity'),
                    'worktable_flatness': params.get('bm_worktable_flatness'),
                    'column_parallelism': params.get('bm_column_parallelism'),
                    'worktable_x_parallelism': params.get('bm_worktable_x_parallelism'),
                    'boring_axis_taper_radial_near': params.get('bm_boring_axis_taper_radial_near'),
                    'boring_axis_taper_radial_300mm': params.get('bm_boring_axis_taper_radial_300mm'),
                    'boring_axis_radial_retracted': params.get('bm_boring_axis_radial_retracted'),
                    'boring_axis_radial_extended': params.get('bm_boring_axis_radial_extended'),
                    'milling_axis_radial': params.get('bm_milling_axis_radial'),
                    'boring_axis_axial_retracted': params.get('bm_boring_axis_axial_retracted'),
                    'milling_axis_axial': params.get('bm_milling_axis_axial'),
                    'linear_axis_repeatability_x': params.get('bm_linear_axis_repeatability_x'),
                    'linear_axis_repeatability_y': params.get('bm_linear_axis_repeatability_y'),
                    'linear_axis_repeatability_z': params.get('bm_linear_axis_repeatability_z'),
                    'linear_axis_repeatability_w': params.get('bm_linear_axis_repeatability_w'),
                    'linear_axis_positioning_accuracy_x': params.get('bm_linear_axis_positioning_accuracy_x'),
                    'linear_axis_positioning_accuracy_y': params.get('bm_linear_axis_positioning_accuracy_y'),
                    'linear_axis_positioning_accuracy_z': params.get('bm_linear_axis_positioning_accuracy_z'),
                    'linear_axis_positioning_accuracy_w': params.get('bm_linear_axis_positioning_accuracy_w'),
                    'linear_axis_mean_deviation_x': params.get('bm_linear_axis_mean_deviation_x'),
                    'linear_axis_mean_deviation_y': params.get('bm_linear_axis_mean_deviation_y'),
                    'linear_axis_mean_deviation_z': params.get('bm_linear_axis_mean_deviation_z'),
                    'linear_axis_mean_deviation_w': params.get('bm_linear_axis_mean_deviation_w'),
                    'linear_axis_system_deviation_x': params.get('bm_linear_axis_system_deviation_x'),
                    'linear_axis_system_deviation_y': params.get('bm_linear_axis_system_deviation_y'),
                    'linear_axis_system_deviation_z': params.get('bm_linear_axis_system_deviation_z'),
                    'linear_axis_system_deviation_w': params.get('bm_linear_axis_system_deviation_w'),
                    'linear_axis_backlash_x': params.get('bm_linear_axis_backlash_x'),
                    'linear_axis_backlash_y': params.get('bm_linear_axis_backlash_y'),
                    'linear_axis_backlash_z': params.get('bm_linear_axis_backlash_z'),
                    'linear_axis_backlash_w': params.get('bm_linear_axis_backlash_w'),
                    'rotary_axis_repeatability_a': params.get('bm_rotary_axis_repeatability_a'),
                    'rotary_axis_repeatability_b': params.get('bm_rotary_axis_repeatability_b'),
                    'rotary_axis_repeatability_c': params.get('bm_rotary_axis_repeatability_c'),
                    'rotary_axis_positioning_accuracy_a': params.get('bm_rotary_axis_positioning_accuracy_a'),
                    'rotary_axis_positioning_accuracy_b': params.get('bm_rotary_axis_positioning_accuracy_b'),
                    'rotary_axis_positioning_accuracy_c': params.get('bm_rotary_axis_positioning_accuracy_c'),
                    'rotary_axis_mean_deviation_a': params.get('bm_rotary_axis_mean_deviation_a'),
                    'rotary_axis_mean_deviation_b': params.get('bm_rotary_axis_mean_deviation_b'),
                    'rotary_axis_mean_deviation_c': params.get('bm_rotary_axis_mean_deviation_c'),
                    'rotary_axis_system_deviation_a': params.get('bm_rotary_axis_system_deviation_a'),
                    'rotary_axis_system_deviation_b': params.get('bm_rotary_axis_system_deviation_b'),
                    'rotary_axis_system_deviation_c': params.get('bm_rotary_axis_system_deviation_c'),
                    'rotary_axis_backlash_a': params.get('bm_rotary_axis_backlash_a'),
                    'rotary_axis_backlash_b': params.get('bm_rotary_axis_backlash_b'),
                    'rotary_axis_backlash_c': params.get('bm_rotary_axis_backlash_c'),
                    'square_a': params.get('bm_square_a'),
                    'square_b': params.get('bm_square_b'),
                    'square_c': params.get('bm_square_c'),
                    'square_d': params.get('bm_square_d'),
                    'square_e': params.get('bm_square_e'),
                    'square_f': params.get('bm_square_f'),
                    'diamond_d': params.get('bm_diamond_d'),
                    'diamond_e': params.get('bm_diamond_e'),
                    'circle_f': params.get('bm_circle_f'),
                    'circle_g': params.get('bm_circle_g'),
                    'boring_hole_h': params.get('bm_boring_hole_h'),
                    'boring_hole_i': params.get('bm_boring_hole_i'),
                    'tool_magazine_positioning_accuracy': params.get('bm_tool_magazine_positioning_accuracy'),
                    'tool_magazine_repeatability': params.get('bm_tool_magazine_repeatability'),
                })
            
            return JsonResponse({
                'success': True,
                'machines': boring_milling_machines,
                'count': len(boring_milling_machines)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'获取镗铣床直线度数据失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def import_entropy_data(request):
    """API: 导入信息熵权重数据"""
    if request.method == 'POST':
        try:
            from .models import EntropyWeight, Machine, DataOperationLog
            import json
            from django.db import transaction
            from datetime import datetime
            
            # 检查是否有文件上传
            if 'file' not in request.FILES:
                return JsonResponse({'success': False, 'error': '请上传JSON文件'})
            
            file = request.FILES['file']
            
            # 读取文件内容
            try:
                import_data = json.load(file)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'JSON文件格式错误'})
            
            # 验证数据完整性
            required_fields = ['machine_id', 'indicator_names', 'input_data', 'entropy_values', 'weights']
            for field in required_fields:
                if field not in import_data:
                    return JsonResponse({'success': False, 'error': f'缺少必要字段: {field}'})
            
            machine_id = import_data['machine_id']
            
            try:
                machine_id = int(machine_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': '机床ID必须是整数'})
            
            # 获取机床对象
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
            
            # 生成新的总ID
            def generate_total_id(machine_id):
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                return f"ENTROPY_{machine_id}_{timestamp}"
            
            # 构建保存数据
            save_data = {
                'evaluator': request.user,
                'machine': machine,
                'total_id': generate_total_id(machine_id),
                'sample_count': import_data.get('sample_count', 0),
                'indicator_names': import_data['indicator_names'],
                'input_data': import_data['input_data'],
                'entropy_values': import_data['entropy_values'],
                'weights': import_data['weights'],
                'tolerance_values': import_data.get('tolerance_values'),
                'standard_values': import_data.get('standard_values'),
                'description': import_data.get('description', '')
            }
            
            # 事务管理
            with transaction.atomic():
                # 先查询后操作
                existing_record = EntropyWeight.objects.filter(machine=machine).first()
                
                if existing_record:
                    # 更新操作
                    existing_record.total_id = save_data['total_id']
                    existing_record.sample_count = save_data['sample_count']
                    existing_record.indicator_names = save_data['indicator_names']
                    existing_record.input_data = save_data['input_data']
                    existing_record.entropy_values = save_data['entropy_values']
                    existing_record.weights = save_data['weights']
                    existing_record.tolerance_values = save_data['tolerance_values']
                    existing_record.standard_values = save_data['standard_values']
                    existing_record.description = save_data['description']
                    existing_record.version += 1
                    existing_record.save()
                    
                    entropy_weight = existing_record
                else:
                    # 创建操作
                    entropy_weight = EntropyWeight.objects.create(**save_data)
                
                # 记录操作日志
                log_data = {
                    'operator': request.user,
                    'action': 'UPDATE' if existing_record else 'INSERT',
                    'table_name': 'EntropyWeight',
                    'record_id': str(entropy_weight.id),
                    'machine_id': machine_id,
                    'ip_address': request.META.get('REMOTE_ADDR', ''),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
                    'notes': f'导入数据 - 机床: {machine.name}',
                    'new_data': {
                        'total_id': entropy_weight.total_id,
                        'sample_count': entropy_weight.sample_count,
                        'indicator_names': entropy_weight.indicator_names
                    }
                }
                DataOperationLog.objects.create(**log_data)
            
            return JsonResponse({
                'success': True,
                'message': '数据导入成功',
                'calculation_id': entropy_weight.id,
                'total_id': entropy_weight.total_id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def save_comprehensive_weight_result(request):
    """API: 保存综合权重计算结果"""
    if request.method == 'POST':
        try:
            from .models import Machine, AHPMatrix
            from apps.data_management.services.dameng_service import DamengDatabaseService
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            from apps.accounts.models import UserProfile

            data = json.loads(request.body)
            machine_id = data.get('machine_id')
            total_score = data.get('total_score', 0)
            total_weight = data.get('total_weight', 0)

            performance_score = data.get('performance_score', 0)
            reliability_score = data.get('reliability_score', 0)
            intelligence_score = data.get('intelligence_score', 0)
            green_score = data.get('green_score', 0)

            precision_score = data.get('precision_score', total_score)

            if machine_id:
                try:
                    existing_record = ComprehensiveWeightResultDameng.objects.filter(machine_id=machine_id).order_by('-updated_at').first()
                    if existing_record:
                        if performance_score == 0 and existing_record.performance_score:
                            performance_score = float(existing_record.performance_score)
                        if reliability_score == 0 and existing_record.reliability_score:
                            reliability_score = float(existing_record.reliability_score)
                        if intelligence_score == 0 and existing_record.intelligence_score:
                            intelligence_score = float(existing_record.intelligence_score)
                        if green_score == 0 and existing_record.green_score:
                            green_score = float(existing_record.green_score)
                except Exception:
                    pass

            ahp_matrix = AHPMatrix.objects.filter(path='综合得分').first()
            if ahp_matrix and ahp_matrix.weights and len(ahp_matrix.weights) == 5:
                weights = ahp_matrix.weights
                # [FIX] 所有分数均为百分制，直接加权计算，不再进行五分制转百分制转换
                final_score = (
                    precision_score * weights[0] +
                    performance_score * weights[1] +
                    reliability_score * weights[2] +
                    intelligence_score * weights[3] +
                    green_score * weights[4]
                )
            else:
                final_score = precision_score

            machine = None
            if machine_id:
                try:
                    machine = Machine.objects.get(id=machine_id)
                except Machine.DoesNotExist:
                    return JsonResponse({'success': False, 'error': '机床不存在'})
            else:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})

            is_admin = False
            if request.user.is_authenticated:
                try:
                    user_profile = request.user.userprofile
                    is_admin = user_profile.is_admin()
                except Exception:
                    pass

            dameng_result = DamengDatabaseService.save_comprehensive_weight_result(
                machine_type=machine.machine_type,
                report_number=machine.report_number or f"RPT_{machine.id}",
                machine_id=machine.id,
                machine_model=machine.model or machine.name or f"Machine_{machine.id}",
                comprehensive_score=final_score,
                total_weight=total_weight,
                precision_score=precision_score,
                performance_score=performance_score,
                reliability_score=reliability_score,
                intelligence_score=intelligence_score,
                green_score=green_score,
                user=request.user.username if request.user.is_authenticated else 'unknown',
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )

            if dameng_result['success']:
                return JsonResponse({
                    'success': True,
                    'message': '综合权重计算结果保存成功',
                    'result_id': dameng_result['data']['id'],
                    'final_score': final_score,
                    'weights_used': weights if ahp_matrix and ahp_matrix.weights else None
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'保存到达梦数据库失败: {dameng_result["message"]}'
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_machine_comprehensive_scores(request):
    """API: 获取机床的五维度得分"""
    if request.method == 'GET':
        try:
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng

            machine_id = request.GET.get('machine_id')
            if not machine_id:
                return JsonResponse({'success': False, 'error': 'machine_id不能为空'})

            try:
                machine_id = int(machine_id)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'machine_id必须是整数'})

            # 权限检查：普通用户只能查询自己创建的机床
            is_admin = False
            try:
                user_profile = request.user.userprofile
                is_admin = user_profile.is_admin()
            except Exception:
                pass

            if not is_admin:
                from .models import Machine
                user_machine_ids = Machine.objects.filter(created_by=request.user).values_list('id', flat=True)
                if machine_id not in user_machine_ids:
                    return JsonResponse({
                        'success': False,
                        'error': '无权访问该机床数据'
                    })

            scores = {
                'precision_score': 0,
                'performance_score': 0,
                'reliability_score': 0,
                'intelligence_score': 0,
                'green_score': 0
            }

            result = ComprehensiveWeightResultDameng.objects.filter(machine_id=machine_id).order_by('-updated_at').first()
            if result:
                scores['precision_score'] = float(result.precision_score) if result.precision_score else 0
                scores['performance_score'] = float(result.performance_score) if result.performance_score else 0
                scores['reliability_score'] = float(result.reliability_score) if result.reliability_score else 0
                scores['intelligence_score'] = float(result.intelligence_score) if result.intelligence_score else 0
                scores['green_score'] = float(result.green_score) if result.green_score else 0

            return JsonResponse({
                'success': True,
                'data': scores
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def save_intelligence_score(request):
    """API: 保存智能化得分 - 支持管理员数据库存储和普通用户本地存储"""
    if request.method == 'POST':
        try:
            from .models import Machine
            from apps.data_management.services.dameng_service import DamengDatabaseService
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            from apps.data_management.excel_import import update_machine_parameters_by_type
            
            data = json.loads(request.body)
            machine_id = data.get('machine_id')
            intelligence_score = data.get('intelligence_score')
            intelligence_checkbox_states = data.get('intelligence_checkbox_states')
            
            # 验证machine_id参数（所有用户都需要提供）
            if not machine_id:
                return JsonResponse({'success': False, 'error': 'machine_id参数不能为空'})
            
            # 验证intelligence_score参数
            if intelligence_score is None or intelligence_score == '':
                return JsonResponse({'success': False, 'error': 'intelligence_score参数不能为空'})
            
            try:
                intelligence_score = float(intelligence_score)
                if intelligence_score < 0 or intelligence_score > 100:
                    return JsonResponse({'success': False, 'error': '智能化得分必须在0-100之间'})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': '智能化得分必须是数字'})
            
            # 获取用户角色
            try:
                user_profile = request.user.userprofile
                is_admin = user_profile.is_admin()
                is_expert = user_profile.is_expert()
            except Exception as e:
                logger.error(f"获取用户角色失败: {str(e)}")
                return JsonResponse({'success': False, 'error': f'获取用户角色失败: {str(e)}'})
            
            # 所有用户：保存到数据库
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
            
            # 保存checkbox状态到机床参数表
            if intelligence_checkbox_states is not None:
                try:
                    machine_info = {
                        'id': machine_id,
                        'machine_type': machine.machine_type,
                        'name': machine.name
                    }
                    parameters = {'intelligence_checkbox_states': intelligence_checkbox_states}
                    result = update_machine_parameters_by_type(DamengDatabaseService, machine_info, parameters, request)
                    if result.get('success'):
                        logger.info(f"智能化checkbox状态保存成功: 机床ID={machine_id}")
                    else:
                        logger.warning(f"智能化checkbox状态保存失败: {result.get('message')}")
                except Exception as e:
                    logger.error(f"保存智能化checkbox状态时发生异常: {str(e)}")
            
            # 检查是否已存在该机床的综合权重结果
            try:
                result = ComprehensiveWeightResultDameng.objects.get(machine_id=machine_id)
                # 更新智能化得分，保留其他维度的得分
                old_intelligence_score = result.intelligence_score
                result.intelligence_score = intelligence_score
                result.updated_at = timezone.now()
                result.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '智能化得分更新成功',
                    'result_id': result.id,
                    'intelligence_score': float(result.intelligence_score),
                    'storage_type': 'database'
                })
            except ComprehensiveWeightResultDameng.DoesNotExist:
                # 如果不存在，创建新记录（使用默认值）
                dameng_result = DamengDatabaseService.save_comprehensive_weight_result(
                    machine_type=machine.machine_type,
                    report_number=machine.report_number or f"RPT_{machine.id}",
                    machine_id=machine.id,
                    machine_model=machine.model or machine.name or f"Machine_{machine.id}",
                    comprehensive_score=0,
                    total_weight=0,
                    precision_score=0,
                    performance_score=0,
                    reliability_score=0,
                    intelligence_score=intelligence_score,
                    green_score=0,
                    user=request.user.username if request.user.is_authenticated else 'unknown',
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
                )
                
                if dameng_result['success']:
                    return JsonResponse({
                        'success': True,
                        'message': '智能化得分保存成功',
                        'result_id': dameng_result['data']['id'],
                        'intelligence_score': intelligence_score,
                        'storage_type': 'database'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'保存到达梦数据库失败: {dameng_result["message"]}'
                    })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def save_reliability_score(request):
    """API: 保存可靠性得分 - 支持管理员数据库存储和普通用户本地存储"""
    if request.method == 'POST':
        try:
            from .models import Machine
            from apps.data_management.services.dameng_service import DamengDatabaseService
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}, 请求体: {request.body[:200]}")
                return JsonResponse({'success': False, 'error': f'JSON格式错误: {str(e)}'})
            
            machine_id = data.get('machine_id')
            reliability_score = data.get('reliability_score')
            
            # 验证machine_id参数（所有用户都需要提供）
            if not machine_id:
                return JsonResponse({'success': False, 'error': 'machine_id参数不能为空'})
            
            # 转换machine_id为整数
            try:
                machine_id = int(machine_id)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'machine_id必须是整数'})
            
            # 验证reliability_score参数
            if reliability_score is None or reliability_score == '':
                return JsonResponse({'success': False, 'error': 'reliability_score参数不能为空'})
            
            try:
                reliability_score = float(reliability_score)
                # [FIX] 修改为百分制评分标准（60-100分）
                if reliability_score < 60 or reliability_score > 100:
                    return JsonResponse({'success': False, 'error': '可靠性得分必须在60-100之间（百分制）'})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': '可靠性得分必须是数字'})
            
            # 获取用户角色
            try:
                user_profile = request.user.userprofile
                is_admin = user_profile.is_admin()
                is_expert = user_profile.is_expert()
            except Exception as e:
                logger.error(f"获取用户角色失败: {str(e)}")
                return JsonResponse({'success': False, 'error': f'获取用户角色失败: {str(e)}'})
            
            # 所有用户：保存到数据库
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
            
            # 获取各子指标得分（可选）
            mtbf_score = data.get('mtbf_score', 0)
            mttr_score = data.get('mttr_score', 0)
            availability_score = data.get('availability_score', 0)
            failure_rate_score = data.get('failure_rate_score', 0)
            consistency_score = data.get('consistency_score', 0)
            precision_retention_score = data.get('precision_retention_score', 0)
            mttf_score = data.get('mttf_score', 0)
            
            # 保存到达梦数据库
            dameng_result = DamengDatabaseService.save_reliability_score(
                machine_type=machine.machine_type,
                report_number=machine.report_number or f"RPT_{machine.id}",
                machine_id=machine.id,
                machine_model=machine.model or machine.name or f"Machine_{machine.id}",
                reliability_score=reliability_score,
                mtbf_score=mtbf_score,
                mttr_score=mttr_score,
                availability_score=availability_score,
                failure_rate_score=failure_rate_score,
                consistency_score=consistency_score,
                precision_retention_score=precision_retention_score,
                mttf_score=mttf_score,
                user=request.user.username if request.user.is_authenticated else 'unknown',
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            
            if dameng_result['success']:
                logger.info(f"用户 {request.user.username} (角色: {user_profile.role}) 成功保存可靠性得分: {reliability_score}分 (机床ID: {machine_id}, 存储类型: 数据库)")
                return JsonResponse({
                    'success': True,
                    'message': '可靠性得分保存成功',
                    'result_id': dameng_result['data']['id'],
                    'reliability_score': float(reliability_score),
                    'storage_type': 'database',
                    'operation': dameng_result['data']['operation']
                })
            else:
                logger.error(f"用户 {request.user.username} (角色: {user_profile.role}) 保存可靠性得分失败: {dameng_result['message']}")
                return JsonResponse({
                    'success': False,
                    'error': f'保存到达梦数据库失败: {dameng_result["message"]}'
                })
                
        except Exception as e:
            logger.error(f"保存可靠性得分异常: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def save_green_score(request):
    """API: 保存绿色化得分 - 支持管理员数据库存储和普通用户本地存储"""
    if request.method == 'POST':
        try:
            from .models import Machine
            from apps.data_management.services.dameng_service import DamengDatabaseService
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            from apps.data_management.excel_import import update_machine_parameters_by_type

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}, 请求体: {request.body[:200]}")
                return JsonResponse({'success': False, 'error': f'JSON格式错误: {str(e)}'})

            machine_id = data.get('machine_id')
            green_score = data.get('green_score')

            # 验证machine_id参数（所有用户都需要提供）
            if not machine_id:
                return JsonResponse({'success': False, 'error': 'machine_id参数不能为空'})

            # 转换machine_id为整数
            try:
                machine_id = int(machine_id)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'machine_id必须是整数'})

            # 验证green_score参数
            if green_score is None or green_score == '':
                return JsonResponse({'success': False, 'error': 'green_score参数不能为空'})

            try:
                green_score = float(green_score)
                # [FIX] 修改为百分制评分标准（60-100分）
                if green_score < 60 or green_score > 100:
                    return JsonResponse({'success': False, 'error': '绿色化得分必须在60-100之间（百分制）'})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': '绿色化得分必须是数字'})

            # 获取各子指标得分（可选）
            cutting_fluid_score = data.get('cutting_fluid_score', 0)
            lubricant_score = data.get('lubricant_score', 0)
            lightweight_score = data.get('lightweight_score', 0)
            energy_score = data.get('energy_score', 0)
            workpiece_score = data.get('workpiece_score', 0)
            volume_score = data.get('volume_score', 0)
            standby_score = data.get('standby_score', 0)
            idle_score = data.get('idle_score', 0)
            cutting_score = data.get('cutting_score', 0)
            cutting_energy_score = data.get('cutting_energy_score', 0)

            # 获取用户角色
            try:
                user_profile = request.user.userprofile
                is_admin = user_profile.is_admin()
                is_expert = user_profile.is_expert()
            except Exception as e:
                logger.error(f"获取用户角色失败: {str(e)}")
                return JsonResponse({'success': False, 'error': f'获取用户角色失败: {str(e)}'})

            # 所有用户：保存到数据库
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
            
            # 保存绿色化模块参数到机床参数表
            green_parameters = {}
            if 'cutting_fluid_q' in data:
                green_parameters['cutting_fluid_q'] = data['cutting_fluid_q']
            if 'cutting_fluid_p' in data:
                green_parameters['cutting_fluid_p'] = data['cutting_fluid_p']
            if 'lubricant_l' in data:
                green_parameters['lubricant_l'] = data['lubricant_l']
            if 'lubricant_p' in data:
                green_parameters['lubricant_p'] = data['lubricant_p']
            if 'lubricant_x' in data:
                green_parameters['lubricant_x'] = data['lubricant_x']
            if 'lightweight_items' in data:
                green_parameters['lightweight_items'] = data['lightweight_items']
            if 'est_value' in data:
                green_parameters['est_value'] = data['est_value']
            if 'eu_value' in data:
                green_parameters['eu_value'] = data['eu_value']
            if 'ec_value' in data:
                green_parameters['ec_value'] = data['ec_value']
            if 'n_value' in data:
                green_parameters['n_value'] = data['n_value']
            if 'v_value' in data:
                green_parameters['v_value'] = data['v_value']
            
            if green_parameters:
                try:
                    machine_info = {
                        'id': machine_id,
                        'machine_type': machine.machine_type,
                        'name': machine.name
                    }
                    result = update_machine_parameters_by_type(DamengDatabaseService, machine_info, green_parameters, request)
                    if result.get('success'):
                        logger.info(f"绿色化模块参数保存成功: 机床ID={machine_id}")
                    else:
                        logger.warning(f"绿色化模块参数保存失败: {result.get('message')}")
                except Exception as e:
                    logger.error(f"保存绿色化模块参数时发生异常: {str(e)}")

            # 保存到达梦数据库
            dameng_result = DamengDatabaseService.save_green_score(
                machine_type=machine.machine_type,
                report_number=machine.report_number or f"RPT_{machine.id}",
                machine_id=machine.id,
                machine_model=machine.model or machine.name or f"Machine_{machine.id}",
                green_score=green_score,
                cutting_fluid_score=cutting_fluid_score,
                lubricant_score=lubricant_score,
                lightweight_score=lightweight_score,
                energy_score=energy_score,
                workpiece_score=workpiece_score,
                volume_score=volume_score,
                standby_score=standby_score,
                idle_score=idle_score,
                cutting_score=cutting_score,
                cutting_energy_score=cutting_energy_score,
                user=request.user.username if request.user.is_authenticated else 'unknown',
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )

            if dameng_result['success']:
                logger.info(f"用户 {request.user.username} (角色: {user_profile.role}) 成功保存绿色化得分: {green_score}分 (机床ID: {machine_id}, 存储类型: 数据库)")
                return JsonResponse({
                    'success': True,
                    'message': '绿色化得分保存成功',
                    'result_id': dameng_result['data']['id'],
                    'green_score': float(green_score),
                    'storage_type': 'database',
                    'operation': dameng_result['data']['operation']
                })
            else:
                logger.error(f"用户 {request.user.username} (角色: {user_profile.role}) 保存绿色化得分失败: {dameng_result['message']}")
                return JsonResponse({
                    'success': False,
                    'error': f'保存到达梦数据库失败: {dameng_result["message"]}'
                })

        except Exception as e:
            logger.error(f"保存绿色化得分异常: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def ahp_matrix(request):
    """AHP判断矩阵构建"""
    from .models import Machine
    from django.db.models import Q
    
    # 根据用户角色过滤机床
    # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床（admin_saved=True）
    # 普通用户只能看到自己创建的机床
    user_profile = request.user.userprofile
    if user_profile.is_admin():
        machines = Machine.objects.filter(
            Q(created_by=request.user) | Q(admin_saved=True)
        ).distinct()
    else:
        machines = Machine.objects.filter(created_by=request.user)
    
    context = {
        'title': '专家打分系统 - 层次分析法(AHP)判断矩阵构建',
        'machines': machines
    }
    return render(request, 'evaluation/ahp_matrix.html', context)


@login_required
def ahp_consistency_check(request):
    """API: AHP矩阵一致性检验"""
    if request.method == 'POST':
        try:
            from .algorithms.ahp import calculate_weights_from_matrix
            import numpy as np
            
            data = json.loads(request.body)
            matrix_data = data.get('matrix', [])
            indicator_names = data.get('indicator_names', [])
            
            # 转换为numpy数组
            matrix = np.array(matrix_data)
            
            # 计算权重和一致性检验
            geometric_means, normalized_weights, consistency = calculate_weights_from_matrix(matrix)
            
            # 转换NumPy类型为Python原生类型
            consistency_python = {}
            for key, value in consistency.items():
                if isinstance(value, np.ndarray):
                    consistency_python[key] = value.tolist()
                elif isinstance(value, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
                    consistency_python[key] = int(value)
                elif isinstance(value, (np.float64, np.float16, np.float32)):
                    consistency_python[key] = float(value)
                elif isinstance(value, np.bool_):
                    consistency_python[key] = bool(value)
                else:
                    consistency_python[key] = value
            
            return JsonResponse({
                'success': True,
                'data': {
                    'geometric_means': geometric_means.tolist(),
                    'normalized_weights': normalized_weights.tolist(),
                    'consistency': consistency_python
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def entropy_weight(request):
    """信息熵权重计算"""
    context = {
        'title': '信息熵权重计算',
    }
    return render(request, 'evaluation/entropy_weight.html', context)


@login_required
def tolerance_management(request):
    """允差管理界面"""
    from apps.accounts.models import UserProfile
    user_profile = UserProfile.objects.select_related('user').get(user=request.user)
    is_admin = user_profile.is_admin()
    
    context = {
        'title': '允差管理',
        'is_admin': is_admin,
    }
    return render(request, 'evaluation/tolerance_management.html', context)


@login_required
def comprehensive_weight_calculation(request):
    """综合权重计算"""
    context = {
        'title': '精度分数计算',
    }
    return render(request, 'evaluation/comprehensive_weight_calculation.html', context)


@login_required
def ahp_weight_management(request):
    """AHP权重管理"""
    context = {
        'title': 'AHP权重管理',
    }
    return render(request, 'evaluation/ahp_weight_management.html', context)


@login_required
def update_ahp_weight(request, matrix_id):
    """更新AHP权重"""
    context = {
        'title': '更新AHP权重',
        'matrix_id': matrix_id
    }
    return render(request, 'evaluation/update_ahp_weight.html', context)


@login_required
def comprehensive_weight_calculation(request):
    """综合权重计算"""
    from .models import Machine
    from django.http import HttpResponse
    from django.db.models import Q

    # 根据用户角色过滤机床
    user_profile = request.user.userprofile
    is_admin = user_profile.is_admin()
    if is_admin:
        # 管理员可以看到：1) 自己上传的机床 2) 已保存的机床
        machines = Machine.objects.filter(
            Q(created_by=request.user) | Q(admin_saved=True)
        ).distinct()
    else:
        # 普通用户只能看到自己创建的机床
        machines = Machine.objects.filter(created_by=request.user)

    context = {
        'title': '精度分数计算',
        'machines': machines,
        'is_admin': is_admin,
    }
    response = render(request, 'evaluation/comprehensive_weight_calculation.html', context)
    # 允许iframe加载（X-Frame-Options设置为SAMEORIGIN以保持安全性）
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@login_required
def calculate_comprehensive_weight(request):
    """API: 综合权重计算"""
    if request.method == 'POST':
        try:
            import json
            from .algorithms.comprehensive import comprehensive_weight_calculation as calculate_weights

            # 解析请求数据
            data = json.loads(request.body)

            # 计算综合权重
            result = calculate_weights(data)

            return JsonResponse({'success': True, 'result': result})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def save_alpha_coefficient(request):
    """API: 保存组合系数到数据库"""
    from django.http import JsonResponse
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            alpha_value = data.get('alpha')

            # 验证alpha值
            if alpha_value is None:
                return JsonResponse({'success': False, 'message': '组合系数不能为空'})

            try:
                alpha_value = float(alpha_value)
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'message': '组合系数必须是有效的数字'})

            if alpha_value < 0 or alpha_value > 1:
                return JsonResponse({'success': False, 'message': '组合系数必须在0-1之间'})

            # 保存到数据库
            from .models import SystemSettings

            setting, created = SystemSettings.objects.update_or_create(
                key='default_alpha_coefficient',
                defaults={
                    'value': str(alpha_value),
                    'description': '默认组合系数α，用于AHP与信息熵的加权计算'
                }
            )

            # 同时保存到localStorage作为全局默认值
            return JsonResponse({
                'success': True,
                'message': f'组合系数 {alpha_value} 已保存并设为默认值'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'保存失败: {str(e)}'})

    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


@login_required
def get_alpha_coefficient(request):
    """API: 获取保存的组合系数"""
    from django.http import JsonResponse

    try:
        from .models import SystemSettings

        try:
            setting = SystemSettings.objects.get(key='default_alpha_coefficient')
            alpha_value = float(setting.value)
        except SystemSettings.DoesNotExist:
            alpha_value = None
        except (ValueError, TypeError):
            alpha_value = None

        return JsonResponse({
            'success': True,
            'alpha': alpha_value
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'获取失败: {str(e)}'})


@login_required
def submit_ahp_matrix(request):
    """API: 提交AHP判断矩阵到数据库"""
    if request.method == 'POST':
        try:
            from .models import AHPMatrix, Machine
            from .algorithms.ahp import calculate_weights_from_matrix
            import numpy as np
            
            data = json.loads(request.body)
            matrix_data = data.get('matrix', [])
            indicator_names = data.get('indicator_names', [])
            machine_id = data.get('machine_id', None)
            path = data.get('path', '')
            notes = data.get('notes', '')
            
            # 获取机床对象（可选，不强制要求）
            machine = None
            if machine_id:
                machine = Machine.objects.get(id=machine_id)
            
            # 转换为numpy数组
            matrix = np.array(matrix_data)
            
            # 计算权重和一致性检验
            geometric_means, normalized_weights, consistency = calculate_weights_from_matrix(matrix)
            
            # 转换NumPy类型为Python原生类型
            weights_python = normalized_weights.tolist()
            consistency_python = {}
            for key, value in consistency.items():
                if isinstance(value, np.ndarray):
                    consistency_python[key] = value.tolist()
                elif isinstance(value, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
                    consistency_python[key] = int(value)
                elif isinstance(value, (np.float64, np.float16, np.float32)):
                    consistency_python[key] = float(value)
                elif isinstance(value, np.bool_):
                    consistency_python[key] = bool(value)
                else:
                    consistency_python[key] = value
            
            # 检查一致性
            is_consistent = consistency_python.get('CR', 1.0) < 0.1
            
            # 按路径查找现有记录，如果存在则更新，否则创建新记录
            existing_matrix = AHPMatrix.objects.filter(path=path).first()
            
            if existing_matrix:
                # 更新现有记录
                existing_matrix.evaluator = request.user
                existing_matrix.machine = machine
                existing_matrix.indicator_names = indicator_names
                existing_matrix.matrix_data = matrix_data
                existing_matrix.weights = weights_python
                existing_matrix.consistency = consistency_python
                existing_matrix.is_consistent = is_consistent
                existing_matrix.notes = notes
                existing_matrix.save()
                ahp_matrix = existing_matrix
            else:
                # 创建新记录
                ahp_matrix = AHPMatrix.objects.create(
                    evaluator=request.user,
                    machine=machine,
                    path=path,
                    indicator_names=indicator_names,
                    matrix_data=matrix_data,
                    weights=weights_python,
                    consistency=consistency_python,
                    is_consistent=is_consistent,
                    notes=notes
                )
            
            return JsonResponse({
                'success': True,
                'message': 'AHP判断矩阵已成功提交到数据库',
                'data': {
                    'matrix_id': ahp_matrix.id,
                    'weights': weights_python,
                    'consistency': consistency_python,
                    'is_consistent': is_consistent
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def ahp_weight_management(request):
    """AHP权重管理"""
    from .models import AHPMatrix
    from django.utils import timezone

    search_query = request.GET.get('search', '')

    if search_query:
        matrices = AHPMatrix.objects.filter(
            path__icontains=search_query
        ).order_by('path', '-submitted_at')
    else:
        matrices = AHPMatrix.objects.all().order_by('path', '-submitted_at')

    latest_matrices_by_path = {}
    for matrix in matrices:
        if matrix.path not in latest_matrices_by_path:
            latest_matrices_by_path[matrix.path] = matrix

    all_matrices = list(latest_matrices_by_path.values())

    comprehensive_matrix, created = AHPMatrix.objects.get_or_create(
        path='综合得分',
        defaults={
            'evaluator': request.user,
            'indicator_names': ['精度', '性能', '可靠性', '智能化', '绿色化'],
            'matrix_data': [],
            'weights': [0.263492063, 0.247618078, 0.234920078, 0.136508078, 0.117461703],
            'is_consistent': True,
            'submitted_at': timezone.now()
        }
    )

    if created:
        comprehensive_matrix.save()

    if comprehensive_matrix.path not in latest_matrices_by_path:
        latest_matrices_by_path[comprehensive_matrix.path] = comprehensive_matrix

    all_matrices = list(latest_matrices_by_path.values())

    all_matrices = [comprehensive_matrix] + [m for m in all_matrices if m.path != comprehensive_matrix.path]

    context = {
        'title': 'AHP权重管理',
        'all_matrices': all_matrices,
        'search_query': search_query
    }
    return render(request, 'evaluation/ahp_weight_management.html', context)


@login_required
def add_ahp_weight(request):
    """添加AHP权重"""
    from .models import AHPMatrix

    if request.method == 'POST':
        try:
            path = request.POST.get('path', '').strip()
            indicator_names_str = request.POST.get('indicator_names', '')
            weights_str = request.POST.get('weights', '')

            if not path:
                messages.error(request, '路径不能为空')
                return redirect('add_ahp_weight')

            indicator_names = json.loads(indicator_names_str)
            weights = json.loads(weights_str)

            if not isinstance(indicator_names, list) or not isinstance(weights, list):
                messages.error(request, '指标名称和权重都必须是数组格式')
                return redirect('add_ahp_weight')

            if len(indicator_names) != len(weights):
                messages.error(request, '指标数量与权重数量不一致')
                return redirect('add_ahp_weight')

            AHPMatrix.objects.create(
                evaluator=request.user,
                path=path,
                indicator_names=indicator_names,
                matrix_data=[],
                weights=weights,
                consistency={'CR': 0, 'CI': 0, 'lambda_max': 0},
                is_consistent=True
            )

            messages.success(request, 'AHP权重添加成功')
            return redirect('ahp_weight_management')
        except json.JSONDecodeError as e:
            messages.error(request, f'JSON格式错误：{str(e)}')
            return redirect('add_ahp_weight')
        except Exception as e:
            messages.error(request, f'添加失败：{str(e)}')
            return redirect('add_ahp_weight')

    return render(request, 'evaluation/add_ahp_weight.html')


@login_required
def update_ahp_weight(request, matrix_id):
    """更新AHP权重"""
    from .models import AHPMatrix
    
    matrix = get_object_or_404(AHPMatrix, id=matrix_id)
    
    if request.method == 'POST':
        try:
            # 获取新权重数据
            weights_str = request.POST.get('weights', '')
            weights = json.loads(weights_str)
            
            # 验证权重格式
            if not isinstance(weights, list):
                messages.error(request, '权重格式错误，应为数组格式')
                return redirect('ahp_weight_management')
            
            # 更新权重
            matrix.weights = weights
            matrix.save()
            
            messages.success(request, '权重更新成功')
            return redirect('ahp_weight_management')
        except json.JSONDecodeError:
            messages.error(request, '权重格式错误，无法解析JSON')
            return redirect('ahp_weight_management')
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
            return redirect('ahp_weight_management')

    context = {
        'title': '更新AHP权重',
        'matrix': matrix
    }
    return render(request, 'evaluation/update_ahp_weight.html', context)


@login_required
def delete_ahp_weight(request, matrix_id):
    """删除AHP权重"""
    from .models import AHPMatrix

    if request.method == 'POST':
        try:
            matrix = get_object_or_404(AHPMatrix, id=matrix_id)
            matrix.delete()
            return JsonResponse({'success': True, 'message': '删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': '仅支持POST请求'}, status=405)


def get_ahp_weights(request):
    """API: 获取AHP权重（所有机床共用）"""
    if request.method == 'GET':
        try:
            from .models import AHPMatrix
            
            # 初始化默认权重数据结构
            weights = {
                '三级对二级': {
                    '几何精度': [0.4, 0.3, 0.2, 0.1],
                    '位置精度': [0.272727272727273, 0.246212121212121, 0.136363636363636, 0.166666666666667, 0.0227272727272727, 0.15530303030303],
                    '加工精度': [0.35, 0.35, 0.3],
                    '运动精度': [0.25, 0.25, 0.2, 0.15, 0.15]
                },
                '二级对一级': {
                    '精度': [0.230769230769231, 0.243589743589744, 0.333333333333333, 0.192307692307692]
                },
                '四级对三级': {
                    '几何精度': {
                        '进给轴精度': [0.4, 0.25, 0.2, 0.15],
                        '工作台精度': [0.4, 0.3, 0.3],
                        '主轴精度': [0.2, 0.2, 0.2, 0.2, 0.2],
                        '刀库精度': [0.5, 0.5]
                    },
                    '加工精度': {
                        '微观几何形状误差': [1.0],
                        '加工分散性': [1.0],
                        '工件几何精度': [0.5, 0.5]
                    },
                    '运动精度': {
                        '主轴运动精度': [0.2, 0.2, 0.2, 0.2, 0.2],
                        '多轴联动精度': [0.2, 0.2, 0.2, 0.2, 0.2],
                        '传动精度': [0.25, 0.25, 0.25, 0.25],
                        '热误差': [0.33, 0.33, 0.34],
                        '磨损精度': [0.5, 0.5]
                    }
                }
            }
            
            # 从数据库获取最新的AHP权重数据（所有机床共用）
            # 二级对一级
            ahp_matrix_level2 = AHPMatrix.objects.filter(
                path='精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_level2 and ahp_matrix_level2.weights:
                print(f"从数据库获取到二级对一级的AHP权重: {ahp_matrix_level2.weights}")
                weights['二级对一级']['精度'] = ahp_matrix_level2.weights
            else:
                print("未从数据库获取到二级对一级的AHP权重，使用默认值")
            
            # 三级对二级 - 几何精度
            ahp_matrix_geometry = AHPMatrix.objects.filter(
                path='精度/几何精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_geometry and ahp_matrix_geometry.weights:
                weights['三级对二级']['几何精度'] = ahp_matrix_geometry.weights
            
            # 三级对二级 - 位置精度
            ahp_matrix_position = AHPMatrix.objects.filter(
                path='精度/位置精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_position and ahp_matrix_position.weights:
                weights['三级对二级']['位置精度'] = ahp_matrix_position.weights
            
            # 三级对二级 - 加工精度
            ahp_matrix_processing = AHPMatrix.objects.filter(
                path='精度/加工精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_processing and ahp_matrix_processing.weights:
                weights['三级对二级']['加工精度'] = ahp_matrix_processing.weights
            
            # 三级对二级 - 运动精度
            ahp_matrix_motion = AHPMatrix.objects.filter(
                path='精度/运动精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_motion and ahp_matrix_motion.weights:
                weights['三级对二级']['运动精度'] = ahp_matrix_motion.weights
            
            # 四级对三级 - 几何精度/进给轴精度
            ahp_matrix_feed_axis = AHPMatrix.objects.filter(
                path='精度/几何精度/进给轴精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_feed_axis and ahp_matrix_feed_axis.weights:
                weights['四级对三级']['几何精度']['进给轴精度'] = ahp_matrix_feed_axis.weights
            
            # 四级对三级 - 几何精度/工作台精度
            ahp_matrix_worktable = AHPMatrix.objects.filter(
                path='精度/几何精度/工作台精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_worktable and ahp_matrix_worktable.weights:
                weights['四级对三级']['几何精度']['工作台精度'] = ahp_matrix_worktable.weights
            
            # 四级对三级 - 几何精度/主轴精度
            ahp_matrix_spindle = AHPMatrix.objects.filter(
                path='精度/几何精度/主轴精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_spindle and ahp_matrix_spindle.weights:
                weights['四级对三级']['几何精度']['主轴精度'] = ahp_matrix_spindle.weights
            
            # 四级对三级 - 几何精度/刀库精度
            ahp_matrix_tool_magazine = AHPMatrix.objects.filter(
                path='精度/几何精度/刀库精度'
            ).order_by('-submitted_at').first()
            
            if ahp_matrix_tool_magazine and ahp_matrix_tool_magazine.weights:
                weights['四级对三级']['几何精度']['刀库精度'] = ahp_matrix_tool_magazine.weights
            
            # 四级对三级 - 加工精度相关
            ahp_matrix_processing_micro = AHPMatrix.objects.filter(
                path='精度/加工精度/微观几何形状误差'
            ).order_by('-submitted_at').first()
            if ahp_matrix_processing_micro and ahp_matrix_processing_micro.weights:
                weights['四级对三级']['加工精度']['微观几何形状误差'] = ahp_matrix_processing_micro.weights
            
            ahp_matrix_processing_dispersion = AHPMatrix.objects.filter(
                path='精度/加工精度/加工分散性'
            ).order_by('-submitted_at').first()
            if ahp_matrix_processing_dispersion and ahp_matrix_processing_dispersion.weights:
                weights['四级对三级']['加工精度']['加工分散性'] = ahp_matrix_processing_dispersion.weights
            
            ahp_matrix_processing_geometry = AHPMatrix.objects.filter(
                path='精度/加工精度/工件几何精度'
            ).order_by('-submitted_at').first()
            if ahp_matrix_processing_geometry and ahp_matrix_processing_geometry.weights:
                weights['四级对三级']['加工精度']['工件几何精度'] = ahp_matrix_processing_geometry.weights
            
            # 四级对三级 - 运动精度相关
            ahp_matrix_motion_spindle = AHPMatrix.objects.filter(
                path='精度/运动精度/主轴运动精度'
            ).order_by('-submitted_at').first()
            if ahp_matrix_motion_spindle and ahp_matrix_motion_spindle.weights:
                weights['四级对三级']['运动精度']['主轴运动精度'] = ahp_matrix_motion_spindle.weights
            
            ahp_matrix_motion_multi = AHPMatrix.objects.filter(
                path='精度/运动精度/多轴联动精度'
            ).order_by('-submitted_at').first()
            if ahp_matrix_motion_multi and ahp_matrix_motion_multi.weights:
                weights['四级对三级']['运动精度']['多轴联动精度'] = ahp_matrix_motion_multi.weights
            
            ahp_matrix_motion_transmission = AHPMatrix.objects.filter(
                path='精度/运动精度/传动精度'
            ).order_by('-submitted_at').first()
            if ahp_matrix_motion_transmission and ahp_matrix_motion_transmission.weights:
                weights['四级对三级']['运动精度']['传动精度'] = ahp_matrix_motion_transmission.weights
            
            ahp_matrix_motion_thermal = AHPMatrix.objects.filter(
                path='精度/运动精度/热误差'
            ).order_by('-submitted_at').first()
            if ahp_matrix_motion_thermal and ahp_matrix_motion_thermal.weights:
                weights['四级对三级']['运动精度']['热误差'] = ahp_matrix_motion_thermal.weights
            
            ahp_matrix_motion_wear = AHPMatrix.objects.filter(
                path='精度/运动精度/磨损精度'
            ).order_by('-submitted_at').first()
            if ahp_matrix_motion_wear and ahp_matrix_motion_wear.weights:
                weights['四级对三级']['运动精度']['磨损精度'] = ahp_matrix_motion_wear.weights
            
            # 可靠性相关权重 - 从path='可靠性'的记录中获取
            ahp_reliability = AHPMatrix.objects.filter(
                path='可靠性'
            ).order_by('-submitted_at').first()
            
            if ahp_reliability and ahp_reliability.weights and len(ahp_reliability.weights) >= 7:
                reliability_weights = {
                    'mtbf': ahp_reliability.weights[0],
                    'mttr': ahp_reliability.weights[1],
                    'availability': ahp_reliability.weights[2],
                    'failure_rate': ahp_reliability.weights[3],
                    'consistency': ahp_reliability.weights[4],
                    'precision': ahp_reliability.weights[5],
                    'mttf': ahp_reliability.weights[6]
                }
            else:
                reliability_weights = {
                    'mtbf': 0.1,
                    'mttr': 0.1,
                    'availability': 0.1,
                    'failure_rate': 0.1,
                    'consistency': 0.1,
                    'precision': 0.4,
                    'mttf': 0.1
                }
            
            weights['可靠性'] = reliability_weights
            
            # 绿色化模块权重 - 从数据库获取
            # 绿色化模块板块权重（资源消耗 vs 能源消耗）
            ahp_green = AHPMatrix.objects.filter(
                path='绿色化'
            ).order_by('-submitted_at').first()
            
            green_weights = {
                '绿色化模块': {
                    '资源消耗': 0.4,
                    '能源消耗': 0.6
                },
                '资源消耗': {
                    '切削液消耗': 0.33,
                    '润滑油消耗': 0.33,
                    '轻量化设计': 0.34
                },
                '能源消耗': {
                    '有效能量利用率': 0.15,
                    '工件比能': 0.15,
                    '体积比能': 0.15,
                    '待机能耗率': 0.15,
                    '空运转能耗率': 0.15,
                    '切削能耗率': 0.15,
                    '切削能量能耗率': 0.10
                }
            }
            
            if ahp_green and ahp_green.weights and len(ahp_green.weights) >= 2:
                green_weights['绿色化模块']['资源消耗'] = ahp_green.weights[0]
                green_weights['绿色化模块']['能源消耗'] = ahp_green.weights[1]
            
            # 资源消耗子项权重
            ahp_resource = AHPMatrix.objects.filter(
                path='绿色化/资源循环与耗材'
            ).order_by('-submitted_at').first()
            
            if ahp_resource and ahp_resource.weights:
                resource_weights = ahp_resource.weights
                if len(resource_weights) >= 3:
                    green_weights['资源消耗']['切削液消耗'] = resource_weights[0]
                    green_weights['资源消耗']['润滑油消耗'] = resource_weights[1]
                    green_weights['资源消耗']['轻量化设计'] = resource_weights[2]
                elif len(resource_weights) == 2:
                    green_weights['资源消耗']['切削液消耗'] = resource_weights[0]
                    green_weights['资源消耗']['润滑油消耗'] = resource_weights[1]
                    green_weights['资源消耗']['轻量化设计'] = 1 - resource_weights[0] - resource_weights[1]
            
            # 能源消耗子项权重
            ahp_energy = AHPMatrix.objects.filter(
                path='绿色化/能源-能效'
            ).order_by('-submitted_at').first()
            
            if ahp_energy and ahp_energy.weights:
                energy_weights = ahp_energy.weights
                if len(energy_weights) >= 7:
                    green_weights['能源消耗']['有效能量利用率'] = energy_weights[0]
                    green_weights['能源消耗']['工件比能'] = energy_weights[1]
                    green_weights['能源消耗']['体积比能'] = energy_weights[2]
                    green_weights['能源消耗']['待机能耗率'] = energy_weights[3]
                    green_weights['能源消耗']['空运转能耗率'] = energy_weights[4]
                    green_weights['能源消耗']['切削能耗率'] = energy_weights[5]
                    green_weights['能源消耗']['切削能量能耗率'] = energy_weights[6]
            
            weights['绿色化'] = green_weights
            
            return JsonResponse({'success': True, 'weights': weights})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_min_score_error_and_tolerance(request):
    """
    API: 获取机床最低分数对应的误差值和允差
    
    从信息熵计算矩阵中提取各机床在其对应组别中的最低分数值及其关联的允差参数。
    建立机床与信息熵计算矩阵中不同组别的准确映射关系。
    """
    if request.method == 'GET':
        try:
            from django.db import connection
            from .models import Machine
            import json
            
            machine_id = request.GET.get('machine_id')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '机床ID不能为空'})
            
            print(f"获取机床ID {machine_id} 的最低分数误差值和允差数据")
            
            try:
                machine = Machine.objects.get(id=machine_id)
                machine_type = machine.machine_type
                print(f"机床ID {machine_id} 对应的机床类型: {machine_type}")
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'机床ID {machine_id} 不存在'})
            
            result = {
                'error_values': {},
                'tolerance_values': {}
            }
            
            precision_type_mapping = {
                'feed_axis': ('几何精度', '进给轴精度', ['直线度', '平行度', '角度误差', '垂直度']),
                'worktable': ('几何精度', '工作台精度', ['平面度', '直线度', 'T型槽平行度']),
                'spindle': ('几何精度', '主轴精度', ['圆度', '同轴度', '主轴径向跳动', '主轴端面跳动', '主轴轴向窜动']),
                'tool_magazine': ('几何精度', '刀库精度', ['刀库定位精度', '刀库重复定位精度']),
                'position': ('位置精度', None, ['重复定位精度', '定位精度', '平均位置偏移', '定位系统偏差', '最小分辨率', '反向间隙']),
                'workpiece_geometry': ('加工精度', '工件几何精度', ['尺寸精度', '形状精度']),
                'spindle_motion': ('运动精度', '主轴运动精度', ['主轴径向误差', '主轴轴向误差', '主轴角度误差', '主轴启停响应时间', '主轴动平衡精度']),
                'multi_axis': ('运动精度', '多轴联动精度', ['平面圆度误差', '多轴同步误差', '轮廓精度', '空间精度', '动态RTCP精度']),
                'transmission': ('运动精度', '传动精度', ['插补轨迹误差', '伺服跟随误差', '高速超调量', '低速爬行量']),
                'thermal_error': ('运动精度', '热误差', ['进给轴热误差', '主轴径向热误差', '主轴轴向热误差']),
                'wear': ('运动精度', '磨损精度', ['刀具磨损', '砂轮磨损'])
            }
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT PRECISION_TYPE, INDICATOR_NAMES, INPUT_DATA, WEIGHTS, TOLERANCE_VALUES, MACHINE_TYPE
                    FROM ENTROPY_WEIGHT_DAMENG
                    WHERE MACHINE_TYPE = %s
                    ORDER BY CALCULATED_AT DESC
                """, [machine_type])
                
                rows = cursor.fetchall()
                print(f"从ENTROPY_WEIGHT_DAMENG表获取到{len(rows)}条记录")
                
                for row in rows:
                    precision_type = row[0]
                    indicator_names_str = row[1]
                    input_data_str = row[2]
                    weights_str = row[3]
                    tolerance_values_str = row[4]
                    
                    try:
                        indicator_names = json.loads(indicator_names_str) if indicator_names_str else []
                        input_data = json.loads(input_data_str) if input_data_str else []
                        weights = json.loads(weights_str) if weights_str else []
                        tolerance_values = json.loads(tolerance_values_str) if tolerance_values_str else []
                    except Exception as e:
                        print(f"解析JSON失败: {precision_type}, 错误: {e}")
                        continue
                    
                    if precision_type not in precision_type_mapping:
                        continue
                    
                    category, subcategory, indicator_list = precision_type_mapping[precision_type]
                    
                    if not input_data or not weights:
                        continue
                    
                    min_weight_index = 0
                    min_weight = float('inf')
                    for i, w in enumerate(weights):
                        w_val = float(w) if w else 0
                        if w_val < min_weight:
                            min_weight = w_val
                            min_weight_index = i
                    
                    min_score_error_values = []
                    min_score_tolerance_values = []
                    
                    for group_data in input_data:
                        group_error_values = []
                        group_tolerance_values = []
                        
                        if precision_type == 'worktable':
                            flatness_error = float(group_data.get('平面度', 0) or 0)
                            straightness_error = float(group_data.get('直线度', 0) or 0)
                            tslot_error = 0
                            
                            group_error_values = [flatness_error, straightness_error, tslot_error]
                            
                            if isinstance(tolerance_values, dict):
                                first_group_tolerances = None
                                for group_key in tolerance_values:
                                    if isinstance(tolerance_values[group_key], dict):
                                        first_group_tolerances = tolerance_values[group_key]
                                        break
                                    else:
                                        first_group_tolerances = tolerance_values
                                        break
                                
                                if first_group_tolerances and isinstance(first_group_tolerances, dict):
                                    flatness_tol = float(first_group_tolerances.get('平面度允差', 0) or 0)
                                    x_parallelism_tol = float(first_group_tolerances.get('X向平行度允差', 0) or 0)
                                    z_parallelism_tol = float(first_group_tolerances.get('Z向平行度允差', 0) or 0)
                                    
                                    original_error_data = group_data.get('原始误差数据', {})
                                    first_group_original = None
                                    if isinstance(original_error_data, dict):
                                        for group_key in original_error_data:
                                            if isinstance(original_error_data[group_key], dict):
                                                first_group_original = original_error_data[group_key]
                                                break
                                            else:
                                                first_group_original = original_error_data
                                                break
                                    
                                    if first_group_original and isinstance(first_group_original, dict):
                                        x_parallelism_error = float(first_group_original.get('X向平行度误差', 0) or 0)
                                        z_parallelism_error = float(first_group_original.get('Z向平行度误差', 0) or 0)
                                    else:
                                        x_parallelism_error = straightness_error
                                        z_parallelism_error = straightness_error
                                    
                                    flatness_score = (flatness_tol - abs(flatness_error)) / flatness_tol if flatness_tol > 0 else 0
                                    x_parallelism_score = (x_parallelism_tol - abs(x_parallelism_error)) / x_parallelism_tol if x_parallelism_tol > 0 else 0
                                    z_parallelism_score = (z_parallelism_tol - abs(z_parallelism_error)) / z_parallelism_tol if z_parallelism_tol > 0 else 0
                                    
                                    straightness_tol = x_parallelism_tol if x_parallelism_score <= z_parallelism_score else z_parallelism_tol
                                    
                                    tslot_tol = 0
                                    
                                    group_tolerance_values = [flatness_tol, straightness_tol, tslot_tol]
                                    print(f"工作台精度允差计算: 平面度允差={flatness_tol}, X平行度允差={x_parallelism_tol}, Z平行度允差={z_parallelism_tol}")
                                    print(f"工作台精度原始误差: X平行度误差={x_parallelism_error}, Z平行度误差={z_parallelism_error}")
                                    print(f"工作台精度得分计算: 平面度得分={flatness_score}, X平行度得分={x_parallelism_score}, Z平行度得分={z_parallelism_score}")
                                    print(f"工作台精度直线度允差选择: {'X向平行度允差' if x_parallelism_score <= z_parallelism_score else 'Z向平行度允差'}={straightness_tol}")
                                else:
                                    group_tolerance_values = [0, 0, 0]
                            else:
                                group_tolerance_values = [0, 0, 0]
                        else:
                            for i, indicator_name in enumerate(indicator_names):
                                if indicator_name in group_data:
                                    val = group_data.get(indicator_name, 0)
                                    if isinstance(val, (int, float, str)):
                                        try:
                                            error_val = float(val or 0)
                                            group_error_values.append(error_val)
                                        except (ValueError, TypeError):
                                            pass
                            
                            if isinstance(tolerance_values, dict):
                                for indicator_name in indicator_names:
                                    if indicator_name in tolerance_values:
                                        tol_val = float(tolerance_values[indicator_name] or 0)
                                        group_tolerance_values.append(tol_val)
                            elif isinstance(tolerance_values, list):
                                for tol in tolerance_values:
                                    try:
                                        tol_val = float(tol or 0)
                                        group_tolerance_values.append(tol_val)
                                    except:
                                        pass
                        
                        if group_error_values:
                            min_score_error_values.append(group_error_values)
                        if group_tolerance_values:
                            min_score_tolerance_values.append(group_tolerance_values)
                    
                    if min_score_error_values:
                        if category not in result['error_values']:
                            result['error_values'][category] = {}
                        if subcategory:
                            if subcategory not in result['error_values'][category]:
                                result['error_values'][category][subcategory] = {}
                            for i, indicator_name in enumerate(indicator_names):
                                if i < len(min_score_error_values[0]):
                                    result['error_values'][category][subcategory][indicator_name] = min_score_error_values[0][i]
                        else:
                            for i, indicator_name in enumerate(indicator_names):
                                if i < len(min_score_error_values[0]):
                                    if indicator_name not in result['error_values'][category]:
                                        result['error_values'][category][indicator_name] = []
                                    result['error_values'][category][indicator_name].append(min_score_error_values[0][i])
                    
                    if min_score_tolerance_values:
                        if category not in result['tolerance_values']:
                            result['tolerance_values'][category] = {}
                        if subcategory:
                            if subcategory not in result['tolerance_values'][category]:
                                result['tolerance_values'][category][subcategory] = {}
                            for i, indicator_name in enumerate(indicator_names):
                                if i < len(min_score_tolerance_values[0]):
                                    result['tolerance_values'][category][subcategory][indicator_name] = min_score_tolerance_values[0][i]
                        else:
                            for i, indicator_name in enumerate(indicator_names):
                                if i < len(min_score_tolerance_values[0]):
                                    if indicator_name not in result['tolerance_values'][category]:
                                        result['tolerance_values'][category][indicator_name] = []
                                    result['tolerance_values'][category][indicator_name].append(min_score_tolerance_values[0][i])
            
            print(f"返回的误差值数据: {result['error_values']}")
            print(f"返回的允差数据: {result['tolerance_values']}")
            
            return JsonResponse({'success': True, 'data': result})
            
        except Exception as e:
            print(f"获取最低分数误差值和允差出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def export_evaluation_data(request):
    """导出评价数据到Excel"""
    from django.http import HttpResponse
    from openpyxl import load_workbook, Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    import os
    from datetime import datetime
    import tempfile
    from urllib.parse import quote
    
    if request.method == 'POST':
        tmp_path = None
        try:
            # 解析请求数据
            data = json.loads(request.body)
            machine_id = data.get('machineId')
            machine_type = data.get('machineType', 'machining_center')
            modules = data.get('modules', {})
            
            # 确保machine_id是整数
            try:
                machine_id = int(machine_id)
            except (ValueError, TypeError):
                pass
            
            logger.info(f"开始导出评价数据: 机床ID={machine_id} (类型: {type(machine_id)}), 类型={machine_type}")
            
            # 根据机床类型选择模板
            template_dir = os.path.join(settings.BASE_DIR, 'static', 'templates')
            if machine_type == 'boring_milling_machine':
                template_path = os.path.join(template_dir, '镗铣床评分表.xlsx')
            else:
                template_path = os.path.join(template_dir, '加工中心评分表.xlsx')
            
            logger.info(f"模板路径: {template_path}, 文件存在: {os.path.exists(template_path)}")
            
            # 加载模板文件
            if os.path.exists(template_path):
                wb = load_workbook(template_path)
                logger.info(f"成功加载模板文件: {template_path}")
            else:
                # 如果模板不存在，创建新的工作簿
                wb = Workbook()
                wb.remove(wb.active)
                logger.warning(f"模板文件不存在，创建新工作簿: {template_path}")
            
            # 填充数据到Excel
            # 删除"数据汇总"sheet（如果存在）
            if '数据汇总' in wb.sheetnames:
                del wb['数据汇总']
                logger.info("已删除'数据汇总'sheet")
            
            # 删除多余的机床列，只保留机床1
            def remove_extra_machine_columns(ws, sheet_name):
                """删除多余的机床列，只保留机床1"""
                try:
                    import re
                    # 检查第一行是否有"机床2"等列标题
                    max_col = ws.max_column
                    cols_to_delete = []
                    
                    for col in range(1, max_col + 1):
                        cell_value = ws.cell(row=1, column=col).value
                        if cell_value:
                            # 使用正则表达式匹配"机床X"格式（X是数字）
                            match = re.search(r'机床(\d+)', str(cell_value))
                            if match:
                                machine_num = int(match.group(1))
                                # 如果机床编号大于1，则删除该列
                                if machine_num > 1:
                                    cols_to_delete.append(col)
                    
                    # 从后往前删除列（避免索引变化）
                    for col in reversed(cols_to_delete):
                        ws.delete_cols(col)
                        logger.info(f"在{sheet_name}中删除列{col}")
                    
                    return True
                except Exception as e:
                    logger.warning(f"删除{sheet_name}的多余列失败: {str(e)}")
                    return False
            
            # 删除机床信息sheet中多余的机床行
            if '机床信息' in wb.sheetnames:
                ws = wb['机床信息']
                # 删除第4-12行（机床2-10）
                for row in range(12, 3, -1):
                    ws.delete_rows(row)
                logger.info("已删除机床信息sheet中多余的机床行")
            
            # 删除各模块sheet中多余的机床列
            for sheet_name in wb.sheetnames:
                if sheet_name != '机床信息':
                    remove_extra_machine_columns(wb[sheet_name], sheet_name)
            
            # 特定sheet的特殊处理
            # 1.2 位置精度：删除G列及以后
            if '1.2 位置精度' in wb.sheetnames:
                ws = wb['1.2 位置精度']
                max_col = ws.max_column
                # 删除G列（第7列）及以后的列
                for col in range(max_col, 6, -1):
                    ws.delete_cols(col)
                logger.info("已删除1.2位置精度sheet中G列及以后的列")
            
            # 3.1 平均故障间隔时间：删除第2行以后
            if '3.1 平均故障间隔时间' in wb.sheetnames:
                ws = wb['3.1 平均故障间隔时间']
                max_row = ws.max_row
                for row in range(max_row, 2, -1):
                    ws.delete_rows(row)
                logger.info("已删除3.1平均故障间隔时间sheet中第2行以后的行")
            
            # 3.3 当量故障率：删除第2行以后
            if '3.3 当量故障率' in wb.sheetnames:
                ws = wb['3.3 当量故障率']
                max_row = ws.max_row
                for row in range(max_row, 2, -1):
                    ws.delete_rows(row)
                logger.info("已删除3.3当量故障率sheet中第2行以后的行")
            
            # 3.4 加工一致性：删除第2行以后
            if '3.4 加工一致性' in wb.sheetnames:
                ws = wb['3.4 加工一致性']
                max_row = ws.max_row
                for row in range(max_row, 2, -1):
                    ws.delete_rows(row)
                logger.info("已删除3.4加工一致性sheet中第2行以后的行")
            
            # 3.5 加工精度保持性：删除第2行以后
            if '3.5 加工精度保持性' in wb.sheetnames:
                ws = wb['3.5 加工精度保持性']
                max_row = ws.max_row
                for row in range(max_row, 2, -1):
                    ws.delete_rows(row)
                logger.info("已删除3.5加工精度保持性sheet中第2行以后的行")
            
            # 5.1 资源循环与耗材：将C列的"机床7是否满足"改为"机床1是否满足"
            if '5.1 资源循环与耗材' in wb.sheetnames:
                ws = wb['5.1 资源循环与耗材']
                # 遍历所有行，查找包含"机床7是否满足"的单元格
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.value and '机床7是否满足' in str(cell.value):
                            cell.value = str(cell.value).replace('机床7是否满足', '机床1是否满足')
                            logger.info(f"已将{cell.coordinate}的'机床7是否满足'改为'机床1是否满足'")
                logger.info("已修改5.1资源循环与耗材sheet中的机床编号")
            
            # 填充机床信息
            if '机床信息' in wb.sheetnames:
                ws = wb['机床信息']
                
                # 从数据库读取机床基本信息
                try:
                    from .models import Machine
                    machine = Machine.objects.filter(id=machine_id).first()
                    if machine:
                        # 填充第3行（第一台机床）
                        row = 3
                        ws[f'A{row}'] = '镗铣床' if machine.machine_type == 'boring_milling_machine' else '加工中心'
                        ws[f'B{row}'] = machine.name
                        ws[f'C{row}'] = machine.machine_number or machine_id
                        ws[f'D{row}'] = machine.report_number
                        ws[f'E{row}'] = machine.model or ''
                        ws[f'F{row}'] = machine.manufacturer or ''
                        ws[f'G{row}'] = str(machine.production_date) if machine.production_date else ''
                        ws[f'H{row}'] = machine.x_axis_travel or ''
                        ws[f'I{row}'] = machine.y_axis_travel or ''
                        ws[f'J{row}'] = machine.z_axis_travel or ''
                        ws[f'K{row}'] = machine.worktable_length or ''
                        ws[f'L{row}'] = machine.workpiece_size or ''
                        
                        # 主轴类型转换：英文 -> 中文
                        spindle_type_map = {
                            'integral': '整体主轴',
                            'attached': '附加主轴',
                            '整体主轴': '整体主轴',
                            '附加主轴': '附加主轴',
                        }
                        spindle_type_cn = spindle_type_map.get(machine.spindle_type, machine.spindle_type or '')
                        ws[f'M{row}'] = spindle_type_cn
                        ws[f'N{row}'] = ''
                        
                        logger.info(f"已填充机床信息: {machine.name} (ID: {machine_id}), 主轴类型: {spindle_type_cn}")
                except Exception as e:
                    logger.error(f"读取机床信息失败: {str(e)}")
            
            # 从数据库读取并填充各模块数据
            try:
                from .views_export_helpers import fill_modules_data_from_database, apply_special_sheet_processing
                fill_modules_data_from_database(wb, machine_id, machine_type)
                logger.info("成功从数据库读取并填充各模块数据")
                
                # 应用特殊Sheet处理（如垂直居中等）
                apply_special_sheet_processing(wb)
                logger.info("成功应用特殊Sheet处理")
            except Exception as e:
                logger.error(f"填充模块数据失败: {str(e)}", exc_info=True)
            
            logger.info("数据填充完成")
            
            # 创建临时文件
            tmp_fd, tmp_path = tempfile.mkstemp(suffix='.xlsx')
            os.close(tmp_fd)
            
            logger.info(f"临时文件路径: {tmp_path}")
            
            # 保存Excel到临时文件
            wb.save(tmp_path)
            
            # 检查文件大小
            file_size = os.path.getsize(tmp_path)
            logger.info(f"生成的Excel文件大小: {file_size} 字节")
            
            if file_size == 0:
                raise Exception("生成的Excel文件大小为0")
            
            # 读取文件内容
            with open(tmp_path, 'rb') as f:
                file_content = f.read()
            
            logger.info(f"读取到的文件内容大小: {len(file_content)} 字节")
            
            # 生成文件名（使用URL编码处理中文）
            machine_type_name = '镗铣床' if machine_type == 'boring_milling_machine' else '加工中心'
            filename = f"{machine_type_name}评价数据_{machine_id}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
            encoded_filename = quote(filename)
            
            # 返回文件
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            # 使用RFC 5987编码处理中文文件名
            response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
            response['Content-Length'] = len(file_content)
            
            logger.info(f"评价数据导出成功: {filename}, 大小: {len(file_content)} 字节")
            return response
            
        except Exception as e:
            logger.error(f"导出评价数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
        finally:
            # 清理临时文件
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                    logger.info(f"已删除临时文件: {tmp_path}")
                except Exception as e:
                    logger.warning(f"删除临时文件失败: {str(e)}")
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def update_machine_parameters_api(request):
    """
    更新机床参数的API端点
    
    功能：
    - 接收机床ID和参数数据
    - 根据机床类型更新对应的参数表
    - 返回更新结果
    
    请求参数：
    - machine_id: 机床ID
    - parameters: 参数字典，包含要更新的字段和值
    - module: 模块名称（可选，用于日志记录）
    
    返回：
    - success: 是否成功
    - message: 结果消息
    - updated_count: 更新的字段数量
    """
    if request.method == 'POST':
        try:
            import json
            from apps.data_management.services.dameng_service import DamengDatabaseService as DamengService
            from apps.data_management.excel_import import update_machine_parameters_by_type
            from .models import Machine
            
            # 解析请求参数
            data = json.loads(request.body)
            machine_id = data.get('machine_id')
            parameters = data.get('parameters', {})
            module = data.get('module', '未知模块')
            
            if not machine_id:
                return JsonResponse({'success': False, 'message': '缺少机床ID'})
            
            if not parameters:
                return JsonResponse({'success': False, 'message': '缺少参数数据'})
            
            # 获取机床信息
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'message': f'机床不存在: {machine_id}'})
            
            # 构造机床信息字典
            machine_info = {
                'id': machine_id,
                'machine_type': machine.machine_type,
                'name': machine.name
            }
            
            # 更新机床参数
            logger.info(f"开始更新机床参数: 机床ID={machine_id}, 模块={module}, 参数数量={len(parameters)}")
            logger.debug(f"更新参数详情: {parameters}")
            
            result = update_machine_parameters_by_type(DamengService, machine_info, parameters, request)
            
            if result.get('success'):
                # 从返回的data中获取更新的字段数量
                updated_fields = result.get('data', {}).get('updated_fields', [])
                updated_count = len(updated_fields)
                logger.info(f"机床参数更新成功: 机床ID={machine_id}, 模块={module}, 更新字段数={updated_count}, 更新字段={updated_fields}")
                return JsonResponse({
                    'success': True,
                    'message': f'参数更新成功',
                    'updated_count': updated_count,
                    'updated_fields': updated_fields
                })
            else:
                error_msg = result.get('message', '未知错误')
                logger.error(f"机床参数更新失败: 机床ID={machine_id}, 模块={module}, 错误={error_msg}")
                return JsonResponse({
                    'success': False,
                    'message': f'参数更新失败: {error_msg}'
                })
                
        except Exception as e:
            logger.error(f"更新机床参数时发生异常: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'更新失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '仅支持POST请求'})




