from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import json
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


@login_required
def report_list(request):
    """报告列表 - 展示所有已生成的评价报告"""
    from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
    from apps.evaluation.models import Machine, UserEvaluationResult
    from apps.accounts.models import UserProfile
    
    user_profile = UserProfile.objects.select_related('user').get(user=request.user)
    is_admin = user_profile.is_admin()
    
    reports = []
    
    if is_admin:
        dameng_reports = ComprehensiveWeightResultDameng.objects.all().order_by('-updated_at')
    else:
        user_machine_ids = Machine.objects.filter(created_by=request.user).values_list('id', flat=True)
        dameng_reports = ComprehensiveWeightResultDameng.objects.filter(
            machine_id__in=user_machine_ids
        ).order_by('-updated_at')
    
    for report in dameng_reports:
        grade = calculate_grade(float(report.comprehensive_score))
        
        # 获取机床详细信息
        machine = Machine.objects.filter(id=report.machine_id).select_related('created_by').first()
        
        # 获取上传用户信息
        upload_user = '未知'
        if machine and machine.created_by:
            upload_user = machine.created_by.get_full_name() or machine.created_by.username
        elif report.evaluator:
            upload_user = report.evaluator
        
        reports.append({
            'id': report.id,
            'report_number': report.report_number,
            'machine_model': report.machine_model,
            'machine_type': report.get_machine_type_display(),
            'machine_type_code': report.machine_type,
            'comprehensive_score': float(report.comprehensive_score),
            'precision_score': float(report.precision_score) if report.precision_score else 0,
            'performance_score': float(report.performance_score) if report.performance_score else 0,
            'reliability_score': float(report.reliability_score) if report.reliability_score else 0,
            'intelligence_score': float(report.intelligence_score) if report.intelligence_score else 0,
            'green_score': float(report.green_score) if report.green_score else 0,
            'grade': grade,
            'evaluator': report.evaluator,
            'updated_at': report.updated_at,
            'machine_id': report.machine_id,
            # 机床详细信息
            'machine_name': machine.name if machine else '-',
            'machine_number': machine.machine_number if machine else '-',
            'model': machine.model if machine else '-',
            'manufacturer': machine.manufacturer if machine else '-',
            'production_date': machine.production_date if machine else None,
            'upload_user': upload_user,
        })
    
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': '报告管理',
        'page_title': '评价报告列表',
        'reports': page_obj,
        'is_admin': is_admin,
        'total_count': len(reports),
    }
    return render(request, 'report/list.html', context)


def calculate_grade(score):
    """根据分数计算等级（A到AAAAA）"""
    if score >= 95:
        return {'level': 'AAAAA', 'name': '', 'color': '#28a745'}
    elif score >= 85:
        return {'level': 'AAAA', 'name': '', 'color': '#20c997'}
    elif score >= 75:
        return {'level': 'AAA', 'name': '', 'color': '#17a2b8'}
    elif score >= 65:
        return {'level': 'AA', 'name': '', 'color': '#ffc107'}
    else:
        return {'level': 'A', 'name': '', 'color': '#dc3545'}


@login_required
def generate_report(request):
    """生成报告页面"""
    from apps.evaluation.models import Machine
    from apps.accounts.models import UserProfile
    
    user_profile = UserProfile.objects.select_related('user').get(user=request.user)
    is_admin = user_profile.is_admin()
    
    if is_admin:
        machines = Machine.objects.filter(
            Q(created_by=request.user) | Q(admin_saved=True)
        ).distinct().select_related('created_by')
    else:
        machines = Machine.objects.filter(created_by=request.user).select_related('created_by')
    
    context = {
        'title': '生成报告',
        'page_title': '生成评价报告',
        'machines': machines,
        'is_admin': is_admin,
    }
    return render(request, 'report/generate.html', context)


@login_required
def report_detail(request, report_id):
    """报告详情页面 - 展示完整的评价报告"""
    from apps.data_management.models_dameng import ComprehensiveWeightResultDameng, MachineParameters, EntropyWeightDameng
    from apps.evaluation.models import Machine
    
    try:
        report = ComprehensiveWeightResultDameng.objects.get(id=report_id)
    except ComprehensiveWeightResultDameng.DoesNotExist:
        messages.error(request, '报告不存在')
        return redirect('report_list')
    
    machine = None
    machine_params = None
    try:
        machine = Machine.objects.get(id=report.machine_id)
        machine_params = MachineParameters.objects.filter(machine_id=report.machine_id).first()
    except Machine.DoesNotExist:
        pass
    
    entropy_weights = EntropyWeightDameng.objects.filter(
        machine_type=report.machine_type
    ).order_by('-calculated_at')
    
    grade = calculate_grade(float(report.comprehensive_score))
    
    radar_data = {
        'labels': ['精度维度', '性能维度', '可靠性维度', '智能化维度', '绿色化维度'],
        'values': [
            float(report.precision_score) if report.precision_score else 0,
            float(report.performance_score) if report.performance_score else 0,
            float(report.reliability_score) if report.reliability_score else 0,
            float(report.intelligence_score) if report.intelligence_score else 0,
            float(report.green_score) if report.green_score else 0,
        ],
        'max': 100
    }
    
    score_distribution = calculate_score_distribution(float(report.comprehensive_score))
    
    recommendations = generate_recommendations(report, machine_params)
    
    context = {
        'title': f'报告详情 - {report.report_number}',
        'page_title': f'评价报告: {report.report_number}',
        'report': report,
        'machine': machine,
        'machine_params': machine_params,
        'entropy_weights': entropy_weights,
        'grade': grade,
        'radar_data': json.dumps(radar_data),
        'score_distribution': score_distribution,
        'recommendations': recommendations,
    }
    return render(request, 'report/detail.html', context)


@login_required
def api_delete_report(request, report_id):
    """API: 删除报告"""
    if request.method == 'POST':
        try:
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            from apps.evaluation.models import Machine
            from apps.accounts.models import UserProfile
            
            report = ComprehensiveWeightResultDameng.objects.get(id=report_id)
            
            user_profile = UserProfile.objects.select_related('user').get(user=request.user)
            is_admin = user_profile.is_admin()
            
            machine = Machine.objects.filter(id=report.machine_id).first()
            
            can_delete = False
            if is_admin:
                can_delete = True
            elif machine and machine.created_by == request.user:
                can_delete = True
            
            if not can_delete:
                return JsonResponse({'success': False, 'error': '无权删除此报告'})
            
            report_number = report.report_number
            report.delete()
            
            logger.info(f"用户 {request.user.username} 删除了报告 {report_number} (ID: {report_id})")
            
            return JsonResponse({
                'success': True,
                'message': '报告删除成功'
            })
            
        except ComprehensiveWeightResultDameng.DoesNotExist:
            return JsonResponse({'success': False, 'error': '报告不存在'})
        except Exception as e:
            logger.error(f"删除报告时出错: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '无效请求方法'})


def calculate_score_distribution(score):
    """计算得分分布区间"""
    if score >= 90:
        return {'range': '90-100分', 'percentile': 95, 'description': '处于行业领先水平'}
    elif score >= 80:
        return {'range': '80-89分', 'percentile': 80, 'description': '处于行业优秀水平'}
    elif score >= 70:
        return {'range': '70-79分', 'percentile': 60, 'description': '处于行业良好水平'}
    elif score >= 60:
        return {'range': '60-69分', 'percentile': 40, 'description': '处于行业合格水平'}
    else:
        return {'range': '60分以下', 'percentile': 20, 'description': '需要改进提升'}


def generate_recommendations(report, machine_params):
    """生成改进建议"""
    recommendations = []
    
    precision_score = float(report.precision_score) if report.precision_score else 0
    if precision_score < 3.5:
        recommendations.append({
            'category': '精度维度',
            'priority': 'high',
            'issue': f'精度得分({precision_score:.1f}分)偏低',
            'suggestion': '建议检查机床几何精度、定位精度等关键指标，必要时进行精度校准或零部件更换。',
            'indicators': ['几何精度', '位置精度', '加工精度']
        })
    elif precision_score < 4.0:
        recommendations.append({
            'category': '精度维度',
            'priority': 'medium',
            'issue': f'精度得分({precision_score:.1f}分)有提升空间',
            'suggestion': '建议定期进行精度检测，关注关键精度指标的变化趋势。',
            'indicators': ['几何精度', '位置精度']
        })
    
    performance_score = float(report.performance_score) if report.performance_score else 0
    if performance_score < 3.5:
        recommendations.append({
            'category': '性能维度',
            'priority': 'high',
            'issue': f'性能得分({performance_score:.1f}分)偏低',
            'suggestion': '建议检查主轴性能、进给系统响应速度等，优化加工参数设置。',
            'indicators': ['主轴性能', '进给系统', '加工效率']
        })
    
    reliability_score = float(report.reliability_score) if report.reliability_score else 0
    if reliability_score < 3.5:
        recommendations.append({
            'category': '可靠性维度',
            'priority': 'medium',
            'issue': f'可靠性得分({reliability_score:.1f}分)偏低',
            'suggestion': '建议加强设备维护保养，建立预防性维护计划，提高设备稳定性。',
            'indicators': ['故障率', 'MTBF', '维护周期']
        })
    
    green_score = float(report.green_score) if report.green_score else 0
    if green_score < 3.5:
        recommendations.append({
            'category': '绿色化维度',
            'priority': 'medium',
            'issue': f'绿色化得分({green_score:.1f}分)偏低',
            'suggestion': '建议优化能耗管理，采用环保冷却液，提高资源利用率。',
            'indicators': ['能耗效率', '环保设计', '资源利用']
        })
    
    intelligence_score = float(report.intelligence_score) if report.intelligence_score else 0
    if intelligence_score < 70:
        recommendations.append({
            'category': '智能化维度',
            'priority': 'medium',
            'issue': f'智能化得分({intelligence_score:.1f}分)偏低',
            'suggestion': '建议升级数控系统，增加传感器配置，提升设备智能化水平。',
            'indicators': ['感知系统', '控制系统', '通信接口']
        })
    
    if not recommendations:
        recommendations.append({
            'category': '综合评价',
            'priority': 'low',
            'issue': '整体表现良好',
            'suggestion': '建议继续保持当前维护水平，定期进行精度检测和性能评估。',
            'indicators': []
        })
    
    return recommendations


@login_required
def api_generate_report(request):
    """API: 生成报告"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            machine_id = data.get('machine_id') or request.POST.get('machine_id')
            report_type = data.get('report_type', 'single')
            report_format = data.get('report_format', 'html')
            
            if not machine_id:
                return JsonResponse({'success': False, 'error': '请选择机床'})
            
            from apps.evaluation.models import Machine
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            
            try:
                machine = Machine.objects.get(id=machine_id)
            except Machine.DoesNotExist:
                return JsonResponse({'success': False, 'error': '机床不存在'})
            
            existing_report = ComprehensiveWeightResultDameng.objects.filter(
                machine_id=machine_id
            ).first()
            
            if existing_report:
                return JsonResponse({
                    'success': True,
                    'message': '报告已存在',
                    'report_id': existing_report.id,
                    'report_number': existing_report.report_number,
                    'redirect_url': f'/reports/{existing_report.id}/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '该机床尚未完成评价，请先进行质量评价',
                    'need_evaluation': True
                })
                
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '无效请求方法'})


@login_required
def api_report_data(request, report_id):
    """API: 获取报告数据"""
    try:
        from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
        
        report = ComprehensiveWeightResultDameng.objects.get(id=report_id)
        
        data = {
            'success': True,
            'report': {
                'id': report.id,
                'report_number': report.report_number,
                'machine_type': report.machine_type,
                'machine_model': report.machine_model,
                'comprehensive_score': float(report.comprehensive_score),
                'precision_score': float(report.precision_score) if report.precision_score else 0,
                'performance_score': float(report.performance_score) if report.performance_score else 0,
                'reliability_score': float(report.reliability_score) if report.reliability_score else 0,
                'intelligence_score': float(report.intelligence_score) if report.intelligence_score else 0,
                'green_score': float(report.green_score) if report.green_score else 0,
                'evaluator': report.evaluator,
                'calculated_at': report.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': report.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        }
        
        return JsonResponse(data)
        
    except ComprehensiveWeightResultDameng.DoesNotExist:
        return JsonResponse({'success': False, 'error': '报告不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_compare_reports(request):
    """API: 报告对比"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_ids = data.get('report_ids', [])
            
            if len(report_ids) < 2:
                return JsonResponse({'success': False, 'error': '请至少选择2个报告进行对比'})
            
            if len(report_ids) > 5:
                return JsonResponse({'success': False, 'error': '最多支持5个报告同时对比'})
            
            from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
            from apps.evaluation.models import Machine
            
            reports = ComprehensiveWeightResultDameng.objects.filter(id__in=report_ids)
            
            comparison_data = []
            for report in reports:
                # 从原始Machine表获取机床名称
                machine_name = None
                try:
                    machine = Machine.objects.get(id=report.machine_id)
                    machine_name = machine.name
                except Machine.DoesNotExist:
                    pass
                
                comparison_data.append({
                    'id': report.id,
                    'report_number': report.report_number,
                    'machine_model': report.machine_model,
                    'machine_name': machine_name,
                    'scores': {
                        'comprehensive': float(report.comprehensive_score),
                        'precision': float(report.precision_score) if report.precision_score else 0,
                        'performance': float(report.performance_score) if report.performance_score else 0,
                        'reliability': float(report.reliability_score) if report.reliability_score else 0,
                        'intelligence': float(report.intelligence_score) if report.intelligence_score else 0,
                        'green': float(report.green_score) if report.green_score else 0,
                    }
                })
            
            return JsonResponse({
                'success': True,
                'reports': comparison_data
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '无效请求方法'})


@login_required
def export_report_pdf(request, report_id):
    """导出报告为PDF"""
    try:
        from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
        
        report = ComprehensiveWeightResultDameng.objects.get(id=report_id)
        
        messages.info(request, 'PDF导出功能开发中，敬请期待')
        return redirect('report_detail', report_id=report_id)
        
    except ComprehensiveWeightResultDameng.DoesNotExist:
        messages.error(request, '报告不存在')
        return redirect('report_list')


@login_required
def export_report_excel(request, report_id):
    """导出报告为Excel"""
    try:
        from apps.data_management.models_dameng import ComprehensiveWeightResultDameng
        import io
        
        report = ComprehensiveWeightResultDameng.objects.get(id=report_id)
        
        messages.info(request, 'Excel导出功能开发中，敬请期待')
        return redirect('report_detail', report_id=report_id)
        
    except ComprehensiveWeightResultDameng.DoesNotExist:
        messages.error(request, '报告不存在')
        return redirect('report_list')
