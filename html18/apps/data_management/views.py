from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.utils import timezone
from django.conf import settings
from apps.accounts.decorators import get_user_queryset
import json
import os
import tempfile
import pandas as pd
from openpyxl import load_workbook
import logging
from datetime import datetime, date

from apps.evaluation.models import Machine
from apps.data_management.models_dameng import MachineParameters, BoringMillingParameters
from apps.data_management.services.dameng_service import DamengDatabaseService

logger = logging.getLogger(__name__)


def parse_year_month(year_month_str):
    """将年月格式(YYYY-MM)转换为日期对象(YYYY-MM-01)，用于DateField存储"""
    if not year_month_str:
        return None
    try:
        # 如果输入是年月格式(YYYY-MM)，添加日期部分并转换为日期对象
        if len(year_month_str) == 7 and '-' in year_month_str:
            return datetime.strptime(f"{year_month_str}-01", '%Y-%m-%d').date()
        # 如果已经是完整日期格式，直接转换
        elif len(year_month_str) == 10:
            return datetime.strptime(year_month_str, '%Y-%m-%d').date()
        return None
    except Exception:
        return None

@login_required
def download_template(request):
    """
    下载机床数据导入模板文件
    """
    # 模板文件路径
    template_dir = os.path.join(settings.BASE_DIR, 'static', 'templates')
    
    # 获取模板类型参数
    template_type = request.GET.get('type', 'machining_center')
    
    # 根据类型选择对应的模板文件
    if template_type == 'boring_milling':
        file_path = os.path.join(template_dir, '镗铣床评分表.xlsx')
        filename = '镗铣床评分表.xlsx'
    else:
        # 默认为加工中心
        file_path = os.path.join(template_dir, '加工中心评分表.xlsx')
        filename = '加工中心评分表.xlsx'

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise Http404(f"模板文件不存在，请联系管理员创建模板文件。查找路径: {file_path}")

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    # 返回文件响应
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # 使用RFC 2231标准处理中文文件名
    from urllib.parse import quote
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{quote(filename)}"
    response['Content-Length'] = file_size
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'

    return response

@login_required
def machine_list(request):
    """机床列表"""
    from apps.accounts.models import UserProfile
    
    # 根据用户角色过滤机床，使用select_related优化查询
    machines = get_user_queryset(
        Machine.objects.select_related('created_by').all(), 
        request.user
    ).order_by('id')
    
    # 检查是否是AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json':
        # 批量获取用户信息，减少数据库查询
        user_ids = {machine.created_by_id for machine in machines if machine.created_by_id}
        user_profiles = UserProfile.objects.filter(user_id__in=user_ids).select_related('user')
        user_profile_map = {profile.user_id: profile for profile in user_profiles}
        
        # 获取机床类型选择映射
        machine_type_choices = dict(Machine._meta.get_field('machine_type').choices)
        
        # 构建机床数据列表
        machine_list = []
        for machine in machines:
            # 获取机床类型显示文本
            machine_type_display = machine_type_choices.get(machine.machine_type, machine.machine_type)
            
            # 获取上传用户信息（使用预查询的数据）
            user_info = None
            if machine.created_by:
                user_profile = user_profile_map.get(machine.created_by_id)
                user_info = {
                    'username': machine.created_by.username,
                    'user_id': f"U{machine.created_by.id:04d}",
                    'full_name': machine.created_by.get_full_name() or machine.created_by.username,
                    'company': user_profile.company if user_profile else '',
                    'phone': user_profile.phone if user_profile else '',
                    'email': machine.created_by.email or ''
                }
            
            machine_data = {
                'id': machine.id,
                'name': machine.name,
                'model': machine.model,
                'report_number': machine.report_number,
                'created_at': machine.created_at.strftime('%Y-%m-%d'),
                'machine_type': machine.machine_type,
                'machine_type_display': machine_type_display,
                'x_axis_travel': float(machine.x_axis_travel) if machine.x_axis_travel else None,
                'y_axis_travel': float(machine.y_axis_travel) if machine.y_axis_travel else None,
                'z_axis_travel': float(machine.z_axis_travel) if machine.z_axis_travel else None,
                'worktable_length': float(machine.worktable_length) if machine.worktable_length else None,
                'workpiece_size': machine.workpiece_size,
                'spindle_type': machine.spindle_type,
                'uploaded_by': user_info
            }
            
            # 添加 admin_saved 字段（如果存在）
            if hasattr(machine, 'admin_saved'):
                machine_data['admin_saved'] = machine.admin_saved
            
            machine_list.append(machine_data)
        
        # 返回JSON响应
        return JsonResponse({
            'success': True,
            'machines': machine_list
        })
    else:
        # 普通请求，返回HTML页面
        context = {
            'title': '机床数据管理',
            'page_title': '机床列表',
            'machines': machines
        }
        return render(request, 'data_management/machine_list.html', context)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def import_data(request):
    """导入数据"""
    from django.http import JsonResponse
    import pandas as pd
    import os
    import re
    from openpyxl import load_workbook
    from apps.evaluation.models import Machine
    from django.utils import timezone
    import tempfile
    import logging
    import traceback
    
    # 配置日志
    logger = logging.getLogger(__name__)
    
    # 辅助函数：从字符串中提取数值
    def extract_number(value):
        """从字符串中提取数值，支持带单位的格式如 '320 mm' 和科学计数法如 '-4E-5'"""
        if value is None or value == '':
            return None
        # 转换为字符串
        value_str = str(value).strip()
        # 使用正则表达式提取数字（包括小数和科学计数法）
        match = re.search(r'[-+]?(?:[0-9]*\.?[0-9]+|[0-9]+\.?[0-9]*)(?:[eE][-+]?[0-9]+)?', value_str)
        if match:
            try:
                num_str = match.group()
                # 统一转换为float以支持科学计数法
                return float(num_str)
            except (ValueError, TypeError):
                return None
        return None
    
    if request.method == 'POST':
        try:
            # 检查是否上传了文件
            if 'data_file' not in request.FILES:
                return JsonResponse({'success': False, 'message': '请选择要导入的文件'})
            
            # 获取上传的文件
            data_file = request.FILES['data_file']
            logger.info(f'开始导入文件: {data_file.name}')
            
            # 验证文件类型
            allowed_extensions = ['.xlsx', '.xls', '.csv']
            file_extension = os.path.splitext(data_file.name)[1].lower()
            
            if file_extension not in allowed_extensions:
                return JsonResponse({'success': False, 'message': '不支持的文件类型，请上传 Excel (.xlsx, .xls) 或 CSV 格式的文件'})
            
            # 存储导入的机床数据
            imported_count = 0
            error_count = 0
            error_messages = []
            
            # 读取文件内容
            if file_extension in ['.xlsx', '.xls']:
                from apps.data_management.excel_import import process_excel_import
                result = process_excel_import(data_file, request, Machine)
                
                if result['success']:
                    imported_count = result.get('imported_count', 0)
                    detection_success = result.get('detection_success_count', 0)
                    detection_failure = result.get('detection_failure_count', 0)
                    module_success = result.get('module_success_count', 0)
                    module_failure = result.get('module_failure_count', 0)
                    errors = result.get('error_messages', [])
                    
                    logger.info(f'导入完成: 成功导入 {imported_count} 台机床，检测项目成功 {detection_success} 条，模块数据成功 {module_success} 项')
                    
                    return JsonResponse({
                        'success': True,
                        'message': result.get('message', f'导入成功！共导入 {imported_count} 台机床。'),
                        'imported_count': imported_count,
                        'detection_success_count': detection_success,
                        'detection_failure_count': detection_failure,
                        'module_success_count': module_success,
                        'module_failure_count': module_failure,
                        'error_messages': errors
                    })
                else:
                    return JsonResponse({'success': False, 'message': result.get('message', '导入失败')})
            elif file_extension == '.csv':
                try:
                    # 尝试读取CSV文件
                    df = pd.read_csv(data_file)
                    logger.info(f'CSV文件包含 {len(df)} 行数据')
                    
                    # 验证CSV文件是否包含必要的关键字
                    # 获取表头行
                    header_row = df.columns.tolist()
                    
                    # 定义预期表头关键字
                    expected_keywords = ['机床类型', '机床型号', '报告编号', '轴线测量行程', '工作台短边', '工件尺寸', '主轴类型', '实测X', '实测Y', '实测Z']
                    
                    # 辅助函数：检查行中是否包含所有预期关键字（忽略None和空字符串）
                    def contains_all_keywords(row, keywords):
                        row_str = [str(cell) if cell is not None else '' for cell in row]
                        for kw in keywords:
                            found = any(kw in cell for cell in row_str)
                            if not found:
                                return False
                        return True
                    
                    # 执行验证
                    if not contains_all_keywords(header_row, expected_keywords):
                        return JsonResponse({'success': False, 'message': 'CSV文件格式不正确，请使用正确的机床信息表模板'})
                    
                    # 解析数据并创建机床记录
                    for row_idx, row in df.iterrows():
                        try:
                            # 提取数据
                            machine_type = row.get('机床类型', '')
                            machine_model = row.get('机床型号', '')
                            report_number = row.get('报告编号', '')
                            x_axis_travel = row.get('实测X', None)
                            y_axis_travel = row.get('实测Y', None)
                            z_axis_travel = row.get('实测Z', None)
                            worktable_short_side = row.get('工作台短边', None)
                            workpiece_size = row.get('工件尺寸', None)
                            spindle_type = row.get('主轴类型', '')
                            machine_number = row.get('机床编号', None)
                            manufacturer = row.get('生产厂家', None)
                            production_date_raw = row.get('生产日期', None)
                            production_date = parse_year_month(production_date_raw) if production_date_raw else None
                            
                            # 转换机床类型为系统内部值
                            machine_type_map = {
                                '加工中心': 'machining_center',
                                '镗铣床': 'boring_milling_machine'
                            }
                            machine_type_internal = machine_type_map.get(machine_type, 'machining_center')
                            
                            # 数据兼容性处理：主轴类型
                            # 处理CSV中可能存在的不同数据形式
                            spindle_type_map = {
                                '整体主轴': 'integral',
                                '附加主轴': 'attached',
                                '皮带传动': 'belt_driven',
                                '齿轮传动': 'gear_driven'
                            }
                            if spindle_type and not pd.isna(spindle_type):
                                # 如果是中文描述，映射到内部值
                                spindle_type_internal = spindle_type_map.get(spindle_type, spindle_type)
                            else:
                                spindle_type_internal = 'integral'  # 默认值
                            
                            # 创建机床记录
                            # 判断是否是管理员创建
                            is_admin = request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')
                            machine = Machine(
                                name=machine_name,
                                model=machine_model,
                                report_number=report_number,
                                machine_number=machine_number,
                                manufacturer=manufacturer,
                                production_date=production_date,
                                machine_type=machine_type_internal,
                                x_axis_travel=extract_number(x_axis_travel),
                                y_axis_travel=extract_number(y_axis_travel),
                                z_axis_travel=extract_number(z_axis_travel),
                                worktable_length=extract_number(worktable_short_side),
                                workpiece_size=workpiece_size,
                                spindle_type=spindle_type_internal,
                                created_by=request.user,
                                created_at=timezone.now(),
                                admin_saved=is_admin
                            )
                            
                            # 保存到数据库
                            machine.save()
                            logger.info(f'成功创建机床: {machine_name} (ID: {machine.id})')
                            
                            # 计算并保存允差值到机床记录
                            try:
                                from apps.evaluation.views import calculate_tolerances_for_group_1
                                
                                # 计算组别1的允差值
                                tolerance_group_1 = calculate_tolerances_for_group_1(
                                    machine_type_internal,
                                    extract_number(x_axis_travel),
                                    extract_number(y_axis_travel),
                                    extract_number(z_axis_travel),
                                    extract_number(worktable_short_side),
                                    workpiece_size,
                                    spindle_type_internal
                                )
                                
                                # 保存允差值到机床记录
                                machine.tolerance_group_1 = tolerance_group_1
                                machine.save()
                                logger.info(f'成功计算并保存允差值: {machine_name} (ID: {machine.id})')
                                
                            except Exception as e:
                                logger.error(f'计算允差值时出错: {str(e)}')
                            
                            imported_count += 1
                            
                        except Exception as e:
                            error_count += 1
                            error_messages.append(f"第{row_idx + 2}行：{str(e)}")
                            logger.error(f'处理第{row_idx + 2}行时出错: {str(e)}')
                    
                    logger.info(f'CSV文件导入完成: 成功 {imported_count}, 失败 {error_count}')
                    
                except Exception as e:
                    logger.error(f'处理CSV文件时出错: {str(e)}')
                    return JsonResponse({'success': False, 'message': f'无法识别该CSV文件: {str(e)}'})
            
            # 生成导入结果消息
            if error_count > 0:
                error_msg = '\n'.join(error_messages[:5])  # 只显示前5个错误
                if len(error_messages) > 5:
                    error_msg += f"\n... 还有 {len(error_messages) - 5} 个错误"
                logger.info(f'导入完成：成功 {imported_count}, 失败 {error_count}')
                return JsonResponse({'success': True, 'message': f'导入完成！成功导入 {imported_count} 条记录，失败 {error_count} 条记录。\n错误信息：\n{error_msg}'})
            else:
                logger.info(f'导入成功：共 {imported_count} 条记录')
                
                # 返回导入的机床数据，供前端保存到localStorage
                imported_machines_result = []
                if imported_count > 0:
                    # 获取最近导入的机床数据
                    # 使用 defer 排除可能不存在的 admin_saved 字段
                    try:
                        recent_machines = Machine.objects.defer('admin_saved').filter(created_by=request.user).order_by('-id')[:imported_count]
                    except Exception:
                        # 如果 defer 失败，使用普通查询
                        recent_machines = Machine.objects.filter(created_by=request.user).order_by('-id')[:imported_count]
                    for machine in recent_machines:
                        imported_machines_result.append({
                            'id': machine.id,
                            'parameters': {
                                'machine_type': machine.machine_type,
                                'x_axis_travel': machine.x_axis_travel,
                                'y_axis_travel': machine.y_axis_travel,
                                'z_axis_travel': machine.z_axis_travel,
                                'worktable_length': machine.worktable_length,
                                'workpiece_size': machine.workpiece_size,
                                'spindle_type': machine.spindle_type
                            }
                        })
                
                return JsonResponse({
                    'success': True, 
                    'message': f'导入成功！共导入 {imported_count} 条机床记录。',
                    'imported_machines': imported_machines_result
                })
            
        except Exception as e:
            logger.error(f'导入过程中出错: {str(e)}')
            return JsonResponse({'success': False, 'message': f'导入失败: {str(e)}'})
    
    # GET请求返回空响应，因为我们使用模态框而不是单独的页面
    return JsonResponse({'success': False, 'message': '无效的请求'})

@login_required
def export_data(request):
    """导出机床数据到Excel - 按机床类型分别导出"""
    from django.http import HttpResponse
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 获取当前用户有权查看的机床数据
        try:
            machines = get_user_queryset(Machine.objects.defer('admin_saved').all(), request.user).select_related('created_by')
        except Exception as e:
            logger.warning(f'无法排除 admin_saved 字段，使用普通查询: {str(e)}')
            machines = get_user_queryset(Machine.objects.all(), request.user).select_related('created_by')
        
        # 过滤未保存的数据，排除管理员上传的数据
        try:
            machines_with_saved = get_user_queryset(Machine.objects.all(), request.user).select_related('created_by')
            unsaved_machines = machines_with_saved.filter(admin_saved=False)
            from apps.accounts.models import UserProfile
            admin_users = UserProfile.objects.filter(role='admin').values_list('user_id', flat=True)
            unsaved_machines = unsaved_machines.exclude(created_by__in=admin_users)
            logger.info(f'开始导出机床数据，共 {machines.count()} 条记录，其中未保存 {unsaved_machines.count()} 条')
        except Exception as filter_error:
            logger.warning(f'admin_saved 字段不存在，导出所有数据: {str(filter_error)}')
            unsaved_machines = machines
        
        if not unsaved_machines.exists():
            return JsonResponse({'success': False, 'message': '没有符合条件的机床数据可以导出'})
        
        # 按机床类型分组
        mc_machines = unsaved_machines.filter(machine_type='machining_center')
        bm_machines = unsaved_machines.filter(machine_type='boring_milling_machine')
        
        # 创建工作簿
        wb = Workbook()
        wb.remove(wb.active)  # 删除默认Sheet
        
        # 定义样式
        header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        unsaved_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
        
        def write_header(ws, headers, row=1):
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col_num)
                cell.value = header
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = thin_border
        
        def style_data_cell(cell, fill=None):
            cell.alignment = cell_alignment
            cell.border = thin_border
            if fill:
                cell.fill = fill
        
        def auto_column_width(ws, col_widths):
            for col_num, width in col_widths.items():
                ws.column_dimensions[get_column_letter(col_num)].width = width
        
        # ==================== 加工中心数据导出 ====================
        if mc_machines.exists():
            # Sheet: 加工中心-机床基本信息
            ws = wb.create_sheet("加工中心-机床基本信息")
            headers = [
                'ID', '机床名称', '机床编号', '报告编号', '规格型号', '生产厂家', '生产日期', '机床类型',
                'X轴行程(mm)', 'Y轴行程(mm)', 'Z轴行程(mm)',
                '工作台长度(mm)', '工件尺寸', '主轴类型',
                '创建时间', '上传用户', '状态'
            ]
            write_header(ws, headers)
            
            for row_num, machine in enumerate(mc_machines, 2):
                data = [
                    machine.id, machine.name or '', machine.machine_number or '',
                    machine.report_number or '', machine.model or '',
                    machine.manufacturer or '',
                    machine.production_date.strftime('%Y-%m') if machine.production_date else '',
                    machine.get_machine_type_display() or '',
                    machine.x_axis_travel or '', machine.y_axis_travel or '',
                    machine.z_axis_travel or '', machine.worktable_length or '',
                    machine.workpiece_size or '', machine.spindle_type or '',
                    machine.created_at.strftime('%Y-%m-%d %H:%M:%S') if machine.created_at else '',
                    machine.created_by.username if machine.created_by else '', '未保存'
                ]
                for col_num, value in enumerate(data, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    style_data_cell(cell, unsaved_fill)
            
            auto_column_width(ws, {i: w for i, w in enumerate([8, 20, 15, 15, 15, 15, 12, 12, 12, 12, 12, 15, 12, 15, 20, 15, 10], 1)})
            ws.row_dimensions[1].height = 30
            ws.freeze_panes = 'A2'
            
            # Sheet: 加工中心-检测项目数据
            try:
                ws2 = wb.create_sheet("加工中心-检测项目数据")
                detection_fields = [
                    ('x_axis_linearity_xy', 'X轴直线度（X-Y垂直平面内）'),
                    ('x_axis_linearity_zx', 'X轴直线度（Z-X水平平面内）'),
                    ('z_axis_linearity_yz', 'Z轴直线度（Y-Z垂直平面内）'),
                    ('z_axis_linearity_zx', 'Z轴直线度（Z-X水平平面内）'),
                    ('y_axis_linearity_xy', 'Y轴直线度（X-Y垂直平面内）'),
                    ('y_axis_linearity_yz', 'Y轴直线度（Y-Z垂直平面内）'),
                    ('x_axis_angle_pitch', 'X轴角度偏差（俯仰）'),
                    ('x_axis_angle_yaw', 'X轴角度偏差（偏摆）'),
                    ('x_axis_angle_roll', 'X轴角度偏差（倾斜）'),
                    ('z_axis_angle_pitch', 'Z轴角度偏差（俯仰）'),
                    ('z_axis_angle_yaw', 'Z轴角度偏差（偏摆）'),
                    ('z_axis_angle_roll', 'Z轴角度偏差（倾斜）'),
                    ('y_axis_angle_yz', 'Y轴角度偏差（Y-Z垂直平面内）'),
                    ('y_axis_angle_xy', 'Y轴角度偏差（X-Y垂直平面内）'),
                    ('y_axis_angle_zx', 'Y轴角度偏差（ZX水平面内）'),
                    ('y_axis_perpendicularity_x', 'Y轴与X轴垂直度'),
                    ('y_axis_perpendicularity_z', 'Y轴与Z轴垂直度'),
                    ('z_axis_perpendicularity_x', 'Z轴与X轴垂直度'),
                    ('spindle_axial_runout', '主轴轴向窜动'),
                    ('spindle_radial_runout_near', '主轴锥孔径向跳动（靠近端部）'),
                    ('spindle_radial_runout_300mm', '主轴锥孔径向跳动（距端部300mm）'),
                    ('spindle_parallelism_yz', '主轴轴线与Z轴平行度（Y-Z平面）'),
                    ('spindle_parallelism_zx', '主轴轴线与Z轴平行度（Z-X平面）'),
                    ('spindle_perpendicularity_x', '主轴轴线与X轴垂直度'),
                    ('spindle_perpendicularity_y', '主轴轴线与Y轴垂直度'),
                    ('worktable_flatness', '工作台面平面度'),
                    ('worktable_parallelism_x', '工作台面与X轴平行度'),
                    ('worktable_parallelism_z', '工作台面与Z轴平行度')
                ]
                headers2 = ['项目编号', '子项', '描述'] + [m.name for m in mc_machines]
                write_header(ws2, headers2)
                
                for row_num, (field_name, display_name) in enumerate(detection_fields, 2):
                    ws2.cell(row=row_num, column=1, value=row_num - 1)
                    ws2.cell(row=row_num, column=2, value='')
                    ws2.cell(row=row_num, column=3, value=display_name)
                    for col_num, machine in enumerate(mc_machines, 4):
                        try:
                            params = MachineParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws2.cell(row=row_num, column=col_num, value=value if value is not None else '')
                        except MachineParameters.DoesNotExist:
                            ws2.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers2) + 1):
                        style_data_cell(ws2.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws2, {1: 10, 2: 10, 3: 30, **{i: 15 for i in range(4, len(headers2) + 1)}})
                ws2.freeze_panes = 'D2'
            except Exception as e:
                logger.error(f'导出加工中心检测项目数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 加工中心-定位精度数据
            try:
                ws3 = wb.create_sheet("加工中心-定位精度数据")
                positioning_fields = [
                    ('linear_axis_repeatability_x', '线性轴X轴-双向重复定位精度'),
                    ('linear_axis_positioning_accuracy_x', '线性轴X轴-双向定位精度'),
                    ('linear_axis_mean_deviation_x', '线性轴X轴-平均双向位置偏差范围'),
                    ('linear_axis_system_deviation_x', '线性轴X轴-双向定位系统偏差E'),
                    ('linear_axis_backlash_x', '线性轴X轴-反向差值'),
                    ('linear_axis_repeatability_y', '线性轴Y轴-双向重复定位精度'),
                    ('linear_axis_positioning_accuracy_y', '线性轴Y轴-双向定位精度'),
                    ('linear_axis_mean_deviation_y', '线性轴Y轴-平均双向位置偏差范围'),
                    ('linear_axis_system_deviation_y', '线性轴Y轴-双向定位系统偏差E'),
                    ('linear_axis_backlash_y', '线性轴Y轴-反向差值'),
                    ('linear_axis_repeatability_z', '线性轴Z轴-双向重复定位精度'),
                    ('linear_axis_positioning_accuracy_z', '线性轴Z轴-双向定位精度'),
                    ('linear_axis_mean_deviation_z', '线性轴Z轴-平均双向位置偏差范围'),
                    ('linear_axis_system_deviation_z', '线性轴Z轴-双向定位系统偏差E'),
                    ('linear_axis_backlash_z', '线性轴Z轴-反向差值'),
                    ('rotary_axis_repeatability_a', '回转轴A轴-双向重复定位精度'),
                    ('rotary_axis_positioning_accuracy_a', '回转轴A轴-双向定位精度'),
                    ('rotary_axis_mean_deviation_a', '回转轴A轴-平均双向位置偏差范围'),
                    ('rotary_axis_system_deviation_a', '回转轴A轴-双向定位系统偏差E'),
                    ('rotary_axis_backlash_a', '回转轴A轴-反向差值'),
                    ('rotary_axis_repeatability_b', '回转轴B轴-双向重复定位精度'),
                    ('rotary_axis_positioning_accuracy_b', '回转轴B轴-双向定位精度'),
                    ('rotary_axis_mean_deviation_b', '回转轴B轴-平均双向位置偏差范围'),
                    ('rotary_axis_system_deviation_b', '回转轴B轴-双向定位系统偏差E'),
                    ('rotary_axis_backlash_b', '回转轴B轴-反向差值'),
                    ('rotary_axis_repeatability_c', '回转轴C轴-双向重复定位精度'),
                    ('rotary_axis_positioning_accuracy_c', '回转轴C轴-双向定位精度'),
                    ('rotary_axis_mean_deviation_c', '回转轴C轴-平均双向位置偏差范围'),
                    ('rotary_axis_system_deviation_c', '回转轴C轴-双向定位系统偏差E'),
                    ('rotary_axis_backlash_c', '回转轴C轴-反向差值')
                ]
                headers3 = ['项目'] + [m.name for m in mc_machines]
                write_header(ws3, headers3)
                
                for row_num, (field_name, display_name) in enumerate(positioning_fields, 2):
                    ws3.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(mc_machines, 2):
                        try:
                            params = MachineParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws3.cell(row=row_num, column=col_num, value=value if value is not None else '')
                        except MachineParameters.DoesNotExist:
                            ws3.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers3) + 1):
                        style_data_cell(ws3.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws3, {1: 30, **{i: 15 for i in range(2, len(headers3) + 1)}})
                ws3.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出加工中心定位精度数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 加工中心-几何精度数据
            try:
                ws4 = wb.create_sheet("加工中心-几何精度数据")
                geometry_fields = [
                    ('cylindricity', '圆柱度'),
                    ('hole_perpendicularity_a', '孔中心轴线与基孔A的垂直度'),
                    ('side_linearity', '侧面的直线度'),
                    ('adjacent_perpendicularity_b', '相邻面与基面B的垂直度'),
                    ('opposite_parallelism_b', '相对面与基面B的平行度'),
                    ('side_linearity_2', '侧面的直线度（第二个）'),
                    ('side_inclination_b', '侧面对基准B的倾斜度'),
                    ('circularity', '圆度'),
                    ('concentricity_c', '外圆和内圆孔C的同心度'),
                    ('slope_linearity', '斜面的直线度'),
                    ('slope_inclination_b', '3°角斜面对基准B的倾斜度'),
                    ('hole_position_c', '孔相对于内孔C的位置度'),
                    ('concentricity_d', '内孔与外孔D的同心度')
                ]
                headers4 = ['项目'] + [m.name for m in mc_machines]
                write_header(ws4, headers4)
                
                for row_num, (field_name, display_name) in enumerate(geometry_fields, 2):
                    ws4.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(mc_machines, 2):
                        try:
                            params = MachineParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws4.cell(row=row_num, column=col_num, value=value if value is not None else '')
                        except MachineParameters.DoesNotExist:
                            ws4.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers4) + 1):
                        style_data_cell(ws4.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws4, {1: 30, **{i: 15 for i in range(2, len(headers4) + 1)}})
                ws4.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出加工中心几何精度数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 加工中心-性能模块数据
            try:
                ws5 = wb.create_sheet("加工中心-性能模块数据")
                performance_fields = [
                    # 加工性能
                    ('cp_value', 'CP值'),
                    ('peak_speed', '峰值转速'),
                    ('valley_speed', '谷值转速'),
                    ('design_max_speed', '设计最大转速'),
                    ('max_fast_speed', '最高快移速度'),
                    ('design_max_fast_speed', '设计最高速度'),
                    ('repeat_positioning_accuracy', '最高速度下重复定位精度'),
                    ('max_feed_speed', '最大进给速度'),
                    ('target_max_speed', '目标最高速度'),
                    ('repeat_positioning_accuracy_feed', 'R2及加速度下重复定位精度'),
                    # 刚度
                    ('radial_stiffness', '径向刚度'),
                    ('axial_stiffness', '轴向刚度'),
                    ('radial_machine_type', '径向刚度机床类型'),
                    ('axial_machine_type', '轴向刚度机床类型'),
                    ('cutting_stiffness', '切削刚度'),
                    ('static_stiffness_accept', '合格线'),
                    ('static_stiffness_value', '静刚度 K_s'),
                    # 运行性能
                    ('max_vibration_speed', '最大振动速度'),
                    ('noise_value', '噪声值'),
                    ('noise_machine_type', '噪声机床类型'),
                    ('noise_weight', '重量选择'),
                    ('initial_power', '初检功率'),
                    ('final_power', '终检功率'),
                    ('current_unbalance', '电流不平衡量'),
                    ('current_fluctuation', '电流波动度'),
                    ('voltage_fluctuation_min', '电压波动下限'),
                    ('voltage_fluctuation_max', '电压波动上限'),
                    ('frequency_fluctuation_min', '频率波动下限'),
                    ('frequency_fluctuation_max', '频率波动上限'),
                    ('radial_thermal_displacement', '径向热位移'),
                    ('radial_thermal_gradient', '热平衡梯度 G1'),
                    ('axial_thermal_displacement', '轴向热位移'),
                    ('axial_thermal_gradient', '热平衡梯度 G2'),
                    # 负荷能力
                    ('measured_max_power', '实测主轴最大功率'),
                    ('design_max_power', '设计主轴最大功率'),
                    ('cutting_vibration_speed1', '切削振动速度1'),
                    ('measured_max_torque', '实测主轴最大扭矩'),
                    ('design_max_torque', '设计主轴最大扭矩'),
                    ('cutting_vibration_speed2', '切削振动速度2'),
                    ('actual_load_weight', '试验实际负重'),
                    ('max_design_weight', '最大设计重量'),
                    ('actual_load_velocity', '试验运行速度'),
                    ('max_design_velocity', '最大设计速度'),
                    ('cutting_vibration_speed3', '切削振动速度3'),
                    ('cutting_vibration_speed4', '切削振动速度4'),
                    ('load_machine_type', '负荷能力机床类型'),
                    ('evaluation_scheme', '评价方案'),
                    ('max_cutting_width', '最大切削宽度'),
                    ('tool_diameter', '刀具直径'),
                    ('max_cutting_length', '最大切削长度'),
                    ('expected_cutting_length', '预期切削长度'),
                    ('max_length_diameter_ratio', '最大径长比'),
                    ('design_length_diameter_ratio', '设计径长比'),
                ]
                headers5 = ['项目'] + [m.name for m in mc_machines]
                write_header(ws5, headers5)
                
                for row_num, (field_name, display_name) in enumerate(performance_fields, 2):
                    ws5.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(mc_machines, 2):
                        try:
                            params = MachineParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws5.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except MachineParameters.DoesNotExist:
                            ws5.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers5) + 1):
                        style_data_cell(ws5.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws5, {1: 30, **{i: 15 for i in range(2, len(headers5) + 1)}})
                ws5.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出加工中心性能模块数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 加工中心-可靠性模块数据
            try:
                ws6 = wb.create_sheet("加工中心-可靠性模块数据")
                reliability_fields = [
                    # MTBF
                    ('total_run_time', 'MTBF总运行时间'),
                    ('fault_count', 'MTBF故障次数'),
                    # MTTR
                    ('repair_time_values', 'MTTR修复时间列表'),
                    # 故障率
                    ('fatal_failure', '致命故障数'),
                    ('serious_failure', '严重故障数'),
                    ('general_failure', '一般故障数'),
                    ('operation_time', '运行时间'),
                    # 加工一致性
                    ('standard_deviation', '标准差'),
                    ('mean_value', '均值'),
                    # 加工精度保持性
                    ('original_precision', '原始精度'),
                    ('failure_precision', '失效精度'),
                    ('initial_precision', '初始精度'),
                    # MTTF
                    ('failure_time_values', 'MTTF故障时间列表'),
                ]
                headers6 = ['项目'] + [m.name for m in mc_machines]
                write_header(ws6, headers6)
                
                for row_num, (field_name, display_name) in enumerate(reliability_fields, 2):
                    ws6.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(mc_machines, 2):
                        try:
                            params = MachineParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws6.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except MachineParameters.DoesNotExist:
                            ws6.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers6) + 1):
                        style_data_cell(ws6.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws6, {1: 30, **{i: 15 for i in range(2, len(headers6) + 1)}})
                ws6.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出加工中心可靠性模块数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 加工中心-智能化模块数据
            try:
                ws7 = wb.create_sheet("加工中心-智能化模块数据")
                intelligence_fields = [
                    ('intelligence_checkbox_states', '智能化checkbox状态'),
                ]
                headers7 = ['项目'] + [m.name for m in mc_machines]
                write_header(ws7, headers7)
                
                for row_num, (field_name, display_name) in enumerate(intelligence_fields, 2):
                    ws7.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(mc_machines, 2):
                        try:
                            params = MachineParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws7.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except MachineParameters.DoesNotExist:
                            ws7.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers7) + 1):
                        style_data_cell(ws7.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws7, {1: 30, **{i: 15 for i in range(2, len(headers7) + 1)}})
                ws7.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出加工中心智能化模块数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 加工中心-绿色化模块数据
            try:
                ws8 = wb.create_sheet("加工中心-绿色化模块数据")
                green_fields = [
                    # 资源循环与耗材
                    ('cutting_fluid_q', '切削液消耗量Q'),
                    ('cutting_fluid_p', '切削液主轴功率P1'),
                    ('lubricant_l', '润滑油消耗量L'),
                    ('lubricant_p', '润滑油主轴功率P2'),
                    ('lubricant_x', '润滑油消耗限定值x'),
                    ('lightweight_items', '轻量化设计项目'),
                    # 能源
                    ('est_value', '待机功率Est'),
                    ('eu_value', '空运转功率Eu'),
                    ('ec_value', '切削功率Ec'),
                    ('n_value', '材料去除率n'),
                    ('v_value', '切削体积v'),
                ]
                headers8 = ['项目'] + [m.name for m in mc_machines]
                write_header(ws8, headers8)
                
                for row_num, (field_name, display_name) in enumerate(green_fields, 2):
                    ws8.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(mc_machines, 2):
                        try:
                            params = MachineParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws8.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except MachineParameters.DoesNotExist:
                            ws8.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers8) + 1):
                        style_data_cell(ws8.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws8, {1: 30, **{i: 15 for i in range(2, len(headers8) + 1)}})
                ws8.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出加工中心绿色化模块数据时发生错误: {str(e)}', exc_info=True)
        
        # ==================== 镗铣床数据导出 ====================
        if bm_machines.exists():
            # Sheet: 镗铣床-机床基本信息
            ws = wb.create_sheet("镗铣床-机床基本信息")
            headers = [
                'ID', '机床名称', '机床编号', '报告编号', '规格型号', '生产厂家', '生产日期', '机床类型',
                '创建时间', '上传用户', '状态'
            ]
            write_header(ws, headers)
            
            for row_num, machine in enumerate(bm_machines, 2):
                data = [
                    machine.id, machine.name or '', machine.machine_number or '',
                    machine.report_number or '', machine.model or '',
                    machine.manufacturer or '',
                    machine.production_date.strftime('%Y-%m') if machine.production_date else '',
                    machine.get_machine_type_display() or '',
                    machine.created_at.strftime('%Y-%m-%d %H:%M:%S') if machine.created_at else '',
                    machine.created_by.username if machine.created_by else '', '未保存'
                ]
                for col_num, value in enumerate(data, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    style_data_cell(cell, unsaved_fill)
            
            auto_column_width(ws, {i: w for i, w in enumerate([8, 20, 15, 15, 15, 15, 12, 12, 20, 15, 10], 1)})
            ws.row_dimensions[1].height = 30
            ws.freeze_panes = 'A2'
            
            # Sheet: 镗铣床-检测项目数据
            try:
                ws2 = wb.create_sheet("镗铣床-检测项目数据")
                bm_detection_fields = [
                    ('bm_column_linearity_yz', '立柱移动的直线度-YZ平面(EYW)'),
                    ('bm_column_linearity_zx', '立柱移动的直线度-ZX平面(EXW)'),
                    ('bm_worktable_x_linearity_xy', '工作台移动(X轴)的直线度-XY平面(EYX)'),
                    ('bm_worktable_x_linearity_zx', '工作台移动(X轴)的直线度-ZX平面(EZX)'),
                    ('bm_spindle_box_y_linearity_yz', '主轴箱移动(Y轴)的直线度-YZ平面(EZY)'),
                    ('bm_spindle_box_y_linearity_xy', '主轴箱移动(Y轴)的直线度-XY平面(EXY)'),
                    ('bm_column_angle_yz', '立柱移动的角度偏差-YZ平面(EAW)'),
                    ('bm_column_angle_zx', '立柱移动的角度偏差-ZX平面(EBW)'),
                    ('bm_column_angle_xy', '立柱移动的角度偏差-XY平面(ECW)'),
                    ('bm_worktable_x_angle_xy', '工作台移动(X轴)的角度偏差-XY平面(ECX)'),
                    ('bm_worktable_x_angle_zx', '工作台移动(X轴)的角度偏差-ZX平面(EBX)'),
                    ('bm_worktable_x_angle_yz', '工作台移动(X轴)的角度偏差-YZ平面(EAX)'),
                    ('bm_spindle_box_y_angle_yz', '主轴箱移动(Y轴)的角度偏差-YZ平面(EAY)'),
                    ('bm_spindle_box_y_angle_zx', '主轴箱移动(Y轴)的角度偏差-ZX平面(EBY)'),
                    ('bm_worktable_x_column_perpendicularity', '工作台移动(X轴)和立柱移动间的垂直度(/1000)'),
                    ('bm_spindle_box_y_worktable_x_perpendicularity', '主轴箱移动(Y轴)对工作台移动(X轴)的垂直度(/1000)'),
                    ('bm_spindle_box_y_column_perpendicularity', '主轴箱移动(Y轴)对立柱移动的垂直度(/1000)'),
                    ('bm_worktable_flatness', '工作台面平面度'),
                    ('bm_column_parallelism', '立柱移动的平行度'),
                    ('bm_worktable_x_parallelism', '工作台移动(X轴)的平行度'),
                    ('bm_boring_axis_taper_radial_near', '镗轴锥孔的径向跳动-靠近轴端部处'),
                    ('bm_boring_axis_taper_radial_300mm', '镗轴锥孔的径向跳动-距镗轴端部300mm处'),
                    ('bm_boring_axis_radial_retracted', '镗轴的径向跳动-镗轴缩回时'),
                    ('bm_boring_axis_radial_extended', '镗轴的径向跳动-镗轴伸出300mm时'),
                    ('bm_milling_axis_radial', '铣轴端部的径向跳动'),
                    ('bm_boring_axis_axial_retracted', '镗轴周期性的轴向窜动-主轴缩回'),
                    ('bm_milling_axis_axial', '铣轴端部的周期性轴向窜动'),
                ]
                headers2 = ['项目编号', '子项', '描述'] + [m.name for m in bm_machines]
                write_header(ws2, headers2)
                
                for row_num, (field_name, display_name) in enumerate(bm_detection_fields, 2):
                    ws2.cell(row=row_num, column=1, value=row_num - 1)
                    ws2.cell(row=row_num, column=2, value='')
                    ws2.cell(row=row_num, column=3, value=display_name)
                    for col_num, machine in enumerate(bm_machines, 4):
                        try:
                            params = BoringMillingParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws2.cell(row=row_num, column=col_num, value=value if value is not None else '')
                        except BoringMillingParameters.DoesNotExist:
                            ws2.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers2) + 1):
                        style_data_cell(ws2.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws2, {1: 10, 2: 10, 3: 40, **{i: 15 for i in range(4, len(headers2) + 1)}})
                ws2.freeze_panes = 'D2'
            except Exception as e:
                logger.error(f'导出镗铣床检测项目数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 镗铣床-定位精度数据
            try:
                ws3 = wb.create_sheet("镗铣床-定位精度数据")
                bm_positioning_fields = [
                    ('bm_linear_axis_repeatability_x', '线性轴X轴双向重复定位精度'),
                    ('bm_linear_axis_positioning_accuracy_x', '线性轴X轴双向定位精度'),
                    ('bm_linear_axis_mean_deviation_x', '线性轴X轴平均双向位置偏差范围'),
                    ('bm_linear_axis_system_deviation_x', '线性轴X轴双向定位系统偏差E'),
                    ('bm_linear_axis_backlash_x', '线性轴X轴反向差值'),
                    ('bm_linear_axis_repeatability_y', '线性轴Y轴双向重复定位精度'),
                    ('bm_linear_axis_positioning_accuracy_y', '线性轴Y轴双向定位精度'),
                    ('bm_linear_axis_mean_deviation_y', '线性轴Y轴平均双向位置偏差范围'),
                    ('bm_linear_axis_system_deviation_y', '线性轴Y轴双向定位系统偏差E'),
                    ('bm_linear_axis_backlash_y', '线性轴Y轴反向差值'),
                    ('bm_linear_axis_repeatability_z', '线性轴Z轴双向重复定位精度'),
                    ('bm_linear_axis_positioning_accuracy_z', '线性轴Z轴双向定位精度'),
                    ('bm_linear_axis_mean_deviation_z', '线性轴Z轴平均双向位置偏差范围'),
                    ('bm_linear_axis_system_deviation_z', '线性轴Z轴双向定位系统偏差E'),
                    ('bm_linear_axis_backlash_z', '线性轴Z轴反向差值'),
                    ('bm_linear_axis_repeatability_w', '线性轴W轴双向重复定位精度'),
                    ('bm_linear_axis_positioning_accuracy_w', '线性轴W轴双向定位精度'),
                    ('bm_linear_axis_mean_deviation_w', '线性轴W轴平均双向位置偏差范围'),
                    ('bm_linear_axis_system_deviation_w', '线性轴W轴双向定位系统偏差E'),
                    ('bm_linear_axis_backlash_w', '线性轴W轴反向差值'),
                    ('bm_rotary_axis_repeatability_a', '回转轴A轴双向重复定位精度'),
                    ('bm_rotary_axis_positioning_accuracy_a', '回转轴A轴双向定位精度'),
                    ('bm_rotary_axis_mean_deviation_a', '回转轴A轴平均双向位置偏差范围'),
                    ('bm_rotary_axis_system_deviation_a', '回转轴A轴双向定位系统偏差E'),
                    ('bm_rotary_axis_backlash_a', '回转轴A轴反向差值'),
                    ('bm_rotary_axis_repeatability_b', '回转轴B轴双向重复定位精度'),
                    ('bm_rotary_axis_positioning_accuracy_b', '回转轴B轴双向定位精度'),
                    ('bm_rotary_axis_mean_deviation_b', '回转轴B轴平均双向位置偏差范围'),
                    ('bm_rotary_axis_system_deviation_b', '回转轴B轴双向定位系统偏差E'),
                    ('bm_rotary_axis_backlash_b', '回转轴B轴反向差值'),
                    ('bm_rotary_axis_repeatability_c', '回转轴C轴双向重复定位精度'),
                    ('bm_rotary_axis_positioning_accuracy_c', '回转轴C轴双向定位精度'),
                    ('bm_rotary_axis_mean_deviation_c', '回转轴C轴平均双向位置偏差范围'),
                    ('bm_rotary_axis_system_deviation_c', '回转轴C轴双向定位系统偏差E'),
                    ('bm_rotary_axis_backlash_c', '回转轴C轴反向差值'),
                ]
                headers3 = ['项目'] + [m.name for m in bm_machines]
                write_header(ws3, headers3)
                
                for row_num, (field_name, display_name) in enumerate(bm_positioning_fields, 2):
                    ws3.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(bm_machines, 2):
                        try:
                            params = BoringMillingParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws3.cell(row=row_num, column=col_num, value=value if value is not None else '')
                        except BoringMillingParameters.DoesNotExist:
                            ws3.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers3) + 1):
                        style_data_cell(ws3.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws3, {1: 35, **{i: 15 for i in range(2, len(headers3) + 1)}})
                ws3.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出镗铣床定位精度数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 镗铣床-几何精度数据（工件几何精度）
            try:
                ws4 = wb.create_sheet("镗铣床-工件几何精度数据")
                bm_geometry_fields = [
                    ('bm_square_a', '正方形-a'),
                    ('bm_square_b', '正方形-b'),
                    ('bm_square_c', '正方形-c'),
                    ('bm_square_d', '正方形-d'),
                    ('bm_square_e', '正方形-e'),
                    ('bm_square_f', '正方形-f'),
                    ('bm_diamond_d', '菱形-d'),
                    ('bm_diamond_e', '菱形-e'),
                    ('bm_circle_f', '圆-f'),
                    ('bm_circle_g', '圆-g'),
                    ('bm_boring_hole_h', '镗孔-h'),
                    ('bm_boring_hole_i', '镗孔-i'),
                ]
                headers4 = ['项目'] + [m.name for m in bm_machines]
                write_header(ws4, headers4)
                
                for row_num, (field_name, display_name) in enumerate(bm_geometry_fields, 2):
                    ws4.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(bm_machines, 2):
                        try:
                            params = BoringMillingParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws4.cell(row=row_num, column=col_num, value=value if value is not None else '')
                        except BoringMillingParameters.DoesNotExist:
                            ws4.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers4) + 1):
                        style_data_cell(ws4.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws4, {1: 30, **{i: 15 for i in range(2, len(headers4) + 1)}})
                ws4.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出镗铣床工件几何精度数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 镗铣床-性能模块数据
            try:
                ws5 = wb.create_sheet("镗铣床-性能模块数据")
                bm_performance_fields = [
                    # 加工性能
                    ('cp_value', 'CP值'),
                    ('peak_speed', '峰值转速'),
                    ('valley_speed', '谷值转速'),
                    ('design_max_speed', '设计最大转速'),
                    ('max_fast_speed', '最高快移速度'),
                    ('design_max_fast_speed', '设计最高速度'),
                    ('repeat_positioning_accuracy', '最高速度下重复定位精度'),
                    ('max_feed_speed', '最大进给速度'),
                    ('target_max_speed', '目标最高速度'),
                    ('repeat_positioning_accuracy_feed', 'R2及加速度下重复定位精度'),
                    # 刚度
                    ('radial_stiffness', '径向刚度'),
                    ('axial_stiffness', '轴向刚度'),
                    ('radial_machine_type', '径向刚度机床类型'),
                    ('axial_machine_type', '轴向刚度机床类型'),
                    ('cutting_stiffness', '切削刚度'),
                    ('static_stiffness_accept', '合格线'),
                    ('static_stiffness_value', '静刚度 K_s'),
                    # 运行性能
                    ('max_vibration_speed', '最大振动速度'),
                    ('noise_value', '噪声值'),
                    ('noise_machine_type', '噪声机床类型'),
                    ('noise_weight', '重量选择'),
                    ('initial_power', '初检功率'),
                    ('final_power', '终检功率'),
                    ('current_unbalance', '电流不平衡量'),
                    ('current_fluctuation', '电流波动度'),
                    ('voltage_fluctuation_min', '电压波动下限'),
                    ('voltage_fluctuation_max', '电压波动上限'),
                    ('frequency_fluctuation_min', '频率波动下限'),
                    ('frequency_fluctuation_max', '频率波动上限'),
                    ('radial_thermal_displacement', '径向热位移'),
                    ('radial_thermal_gradient', '热平衡梯度 G1'),
                    ('axial_thermal_displacement', '轴向热位移'),
                    ('axial_thermal_gradient', '热平衡梯度 G2'),
                    # 负荷能力
                    ('measured_max_power', '实测主轴最大功率'),
                    ('design_max_power', '设计主轴最大功率'),
                    ('cutting_vibration_speed1', '切削振动速度1'),
                    ('measured_max_torque', '实测主轴最大扭矩'),
                    ('design_max_torque', '设计主轴最大扭矩'),
                    ('cutting_vibration_speed2', '切削振动速度2'),
                    ('actual_load_weight', '试验实际负重'),
                    ('max_design_weight', '最大设计重量'),
                    ('actual_load_velocity', '试验运行速度'),
                    ('max_design_velocity', '最大设计速度'),
                    ('cutting_vibration_speed3', '切削振动速度3'),
                    ('cutting_vibration_speed4', '切削振动速度4'),
                    ('load_machine_type', '负荷能力机床类型'),
                    ('evaluation_scheme', '评价方案'),
                    ('max_cutting_width', '最大切削宽度'),
                    ('tool_diameter', '刀具直径'),
                    ('max_cutting_length', '最大切削长度'),
                    ('expected_cutting_length', '预期切削长度'),
                    ('max_length_diameter_ratio', '最大径长比'),
                    ('design_length_diameter_ratio', '设计径长比'),
                ]
                headers5 = ['项目'] + [m.name for m in bm_machines]
                write_header(ws5, headers5)
                
                for row_num, (field_name, display_name) in enumerate(bm_performance_fields, 2):
                    ws5.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(bm_machines, 2):
                        try:
                            params = BoringMillingParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws5.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except BoringMillingParameters.DoesNotExist:
                            ws5.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers5) + 1):
                        style_data_cell(ws5.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws5, {1: 30, **{i: 15 for i in range(2, len(headers5) + 1)}})
                ws5.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出镗铣床性能模块数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 镗铣床-可靠性模块数据
            try:
                ws6 = wb.create_sheet("镗铣床-可靠性模块数据")
                bm_reliability_fields = [
                    # MTBF
                    ('total_run_time', 'MTBF总运行时间'),
                    ('fault_count', 'MTBF故障次数'),
                    # MTTR
                    ('repair_time_values', 'MTTR修复时间列表'),
                    # 故障率
                    ('fatal_failure', '致命故障数'),
                    ('serious_failure', '严重故障数'),
                    ('general_failure', '一般故障数'),
                    ('operation_time', '运行时间'),
                    # 加工一致性
                    ('standard_deviation', '标准差'),
                    ('mean_value', '均值'),
                    # 加工精度保持性
                    ('original_precision', '原始精度'),
                    ('failure_precision', '失效精度'),
                    ('initial_precision', '初始精度'),
                    # MTTF
                    ('failure_time_values', 'MTTF故障时间列表'),
                ]
                headers6 = ['项目'] + [m.name for m in bm_machines]
                write_header(ws6, headers6)
                
                for row_num, (field_name, display_name) in enumerate(bm_reliability_fields, 2):
                    ws6.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(bm_machines, 2):
                        try:
                            params = BoringMillingParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws6.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except BoringMillingParameters.DoesNotExist:
                            ws6.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers6) + 1):
                        style_data_cell(ws6.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws6, {1: 30, **{i: 15 for i in range(2, len(headers6) + 1)}})
                ws6.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出镗铣床可靠性模块数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 镗铣床-智能化模块数据
            try:
                ws7 = wb.create_sheet("镗铣床-智能化模块数据")
                bm_intelligence_fields = [
                    ('intelligence_checkbox_states', '智能化checkbox状态'),
                ]
                headers7 = ['项目'] + [m.name for m in bm_machines]
                write_header(ws7, headers7)
                
                for row_num, (field_name, display_name) in enumerate(bm_intelligence_fields, 2):
                    ws7.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(bm_machines, 2):
                        try:
                            params = BoringMillingParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws7.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except BoringMillingParameters.DoesNotExist:
                            ws7.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers7) + 1):
                        style_data_cell(ws7.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws7, {1: 30, **{i: 15 for i in range(2, len(headers7) + 1)}})
                ws7.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出镗铣床智能化模块数据时发生错误: {str(e)}', exc_info=True)
            
            # Sheet: 镗铣床-绿色化模块数据
            try:
                ws8 = wb.create_sheet("镗铣床-绿色化模块数据")
                bm_green_fields = [
                    # 资源循环与耗材
                    ('cutting_fluid_q', '切削液消耗量Q'),
                    ('cutting_fluid_p', '切削液主轴功率P1'),
                    ('lubricant_l', '润滑油消耗量L'),
                    ('lubricant_p', '润滑油主轴功率P2'),
                    ('lubricant_x', '润滑油消耗限定值x'),
                    ('lightweight_items', '轻量化设计项目'),
                    # 能源
                    ('est_value', '待机功率Est'),
                    ('eu_value', '空运转功率Eu'),
                    ('ec_value', '切削功率Ec'),
                    ('n_value', '材料去除率n'),
                    ('v_value', '切削体积v'),
                ]
                headers8 = ['项目'] + [m.name for m in bm_machines]
                write_header(ws8, headers8)
                
                for row_num, (field_name, display_name) in enumerate(bm_green_fields, 2):
                    ws8.cell(row=row_num, column=1, value=display_name)
                    for col_num, machine in enumerate(bm_machines, 2):
                        try:
                            params = BoringMillingParameters.objects.get(machine_id=machine.id)
                            value = getattr(params, field_name, '')
                            ws8.cell(row=row_num, column=col_num, value=str(value) if value is not None else '')
                        except BoringMillingParameters.DoesNotExist:
                            ws8.cell(row=row_num, column=col_num, value='')
                    for col_num in range(1, len(headers8) + 1):
                        style_data_cell(ws8.cell(row=row_num, column=col_num), unsaved_fill)
                
                auto_column_width(ws8, {1: 30, **{i: 15 for i in range(2, len(headers8) + 1)}})
                ws8.freeze_panes = 'B2'
            except Exception as e:
                logger.error(f'导出镗铣床绿色化模块数据时发生错误: {str(e)}', exc_info=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'机床数据导出_未保存_{timestamp}.xlsx'
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        
        logger.info(f'机床数据导出成功，文件名: {filename}')
        return response
        
    except Exception as e:
        logger.error(f'导出机床数据时发生错误: {str(e)}', exc_info=True)
        return JsonResponse({'success': False, 'message': f'导出失败: {str(e)}'}, status=500)

@login_required
def add_machine(request):
    """添加机床"""
    from apps.evaluation.models import Machine
    from django.contrib import messages
    from django.utils import timezone
    from django.http import JsonResponse
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            name = request.POST.get('name')
            model = request.POST.get('model')
            machine_type = request.POST.get('machine_type')
            
            # 创建新机床
            # 判断是否是管理员创建
            is_admin = request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')
            machine = Machine(
                name=name,
                model=model,
                machine_number=request.POST.get('machine_number'),
                report_number=request.POST.get('report_number'),
                manufacturer=request.POST.get('manufacturer'),
                production_date=parse_year_month(request.POST.get('production_date')),
                machine_type=machine_type,
                created_by=request.user,
                created_at=timezone.now(),
                admin_saved=is_admin
            )
            
            # 处理加工中心特定参数
            if machine_type == 'machining_center':
                machine.x_axis_travel = float(request.POST.get('x_axis_travel', 0)) if request.POST.get('x_axis_travel') else None
                machine.y_axis_travel = float(request.POST.get('y_axis_travel', 0)) if request.POST.get('y_axis_travel') else None
                machine.z_axis_travel = float(request.POST.get('z_axis_travel', 0)) if request.POST.get('z_axis_travel') else None
                
                # 修复工作台长度保存逻辑：确保有值时才更新，避免设置为None
                worktable_length = request.POST.get('worktable_length')
                if worktable_length:
                    machine.worktable_length = float(worktable_length)
                # 如果worktable_length为空，保持原值不变，不设置为None
                
                # 修复工件尺寸保存逻辑：确保有值时才更新，避免设置为None
                workpiece_size = request.POST.get('workpiece_size')
                if workpiece_size:
                    machine.workpiece_size = int(workpiece_size)
                # 如果workpiece_size为空，保持原值不变，不设置为None
                
                machine.spindle_type = request.POST.get('spindle_type')
            
            elif machine_type == 'boring_milling_machine':
                column_measurement_range = request.POST.get('column_measurement_range')
                if column_measurement_range:
                    machine.column_measurement_range = float(column_measurement_range)
                
                worktable_x_range = request.POST.get('worktable_x_range')
                if worktable_x_range:
                    machine.worktable_x_range = float(worktable_x_range)
                
                spindle_box_y_range = request.POST.get('spindle_box_y_range')
                if spindle_box_y_range:
                    machine.spindle_box_y_range = float(spindle_box_y_range)
                
                z_axis_measurement_range = request.POST.get('z_axis_measurement_range')
                if z_axis_measurement_range:
                    machine.z_axis_measurement_range = float(z_axis_measurement_range)
                
                worktable_length_lc = request.POST.get('worktable_length_lc')
                if worktable_length_lc:
                    machine.worktable_length_lc = float(worktable_length_lc)
                
                boring_axis_diameter = request.POST.get('boring_axis_diameter')
                if boring_axis_diameter:
                    machine.boring_axis_diameter = float(boring_axis_diameter)
                
                milling_axis_diameter = request.POST.get('milling_axis_diameter')
                if milling_axis_diameter:
                    machine.milling_axis_diameter = float(milling_axis_diameter)
                
                worktable_type = request.POST.get('worktable_type')
                if worktable_type:
                    machine.worktable_type = worktable_type
                
                machine.spindle_type = None
            
            # 保存到数据库
            machine.save()
            
            # 如果是镗铣床，计算并保存允差到 tolerance_group_1
            if machine_type == 'boring_milling_machine':
                try:
                    from apps.evaluation.views import calculate_boring_milling_tolerances
                    
                    # 计算镗铣床允差值
                    tolerances = calculate_boring_milling_tolerances(
                        machine.column_measurement_range,
                        machine.worktable_x_range,
                        machine.spindle_box_y_range
                    )
                    
                    # 添加工作台平面度允差
                    if machine.worktable_length_lc:
                        if machine.worktable_length_lc <= 1000:
                            flatness_tolerance = 0.030
                        elif machine.worktable_length_lc <= 3000:
                            flatness_tolerance = 0.040
                        elif machine.worktable_length_lc <= 4000:
                            flatness_tolerance = 0.050
                        else:
                            flatness_tolerance = 0.060
                        
                        tolerances['工作台平面度'] = {
                            '允差值': flatness_tolerance,
                            '工作台长边长度': machine.worktable_length_lc
                        }
                    
                    # 添加镗轴直径相关允差
                    if machine.boring_axis_diameter:
                        if machine.boring_axis_diameter <= 125:
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
                                '镗轴直径': machine.boring_axis_diameter
                            },
                            '镗轴的径向跳动': {
                                '允差值': spindle_runout,
                                '镗轴直径': machine.boring_axis_diameter
                            },
                            '周期性的轴向窜动': {
                                '允差值': axial_play,
                                '镗轴直径': machine.boring_axis_diameter
                            }
                        }
                    
                    # 添加铣轴直径相关允差
                    if machine.milling_axis_diameter:
                        if machine.milling_axis_diameter <= 125:
                            milling_axis_runout = 0.010
                            milling_axis_axial_play = 0.010
                        else:
                            milling_axis_runout = 0.015
                            milling_axis_axial_play = 0.015
                        
                        tolerances['铣轴直径相关'] = {
                            '铣轴端部的径向跳动': {
                                '允差值': milling_axis_runout,
                                '铣轴直径': machine.milling_axis_diameter
                            },
                            '铣轴端部的周期性轴向窜动': {
                                '允差值': milling_axis_axial_play,
                                '铣轴直径': machine.milling_axis_diameter
                            }
                        }
                    
                    # 添加工作台类型相关允差
                    if machine.worktable_type:
                        if '任意角度' in machine.worktable_type or '定位' in machine.worktable_type:
                            positioning_accuracy = 18.000
                            repeatability = 10.000
                        else:
                            positioning_accuracy = 11.000
                            repeatability = 6.000
                        
                        tolerances['工作台类型相关'] = {
                            '双向定位精度': {
                                '允差值': positioning_accuracy,
                                '工作台类型': machine.worktable_type
                            },
                            '单向重复定位精度': {
                                '允差值': repeatability,
                                '工作台类型': machine.worktable_type
                            }
                        }
                    
                    # 保存到 tolerance_group_1
                    machine.tolerance_group_1 = {
                        'boring_milling_geometric': tolerances
                    }
                    machine.save()
                    logger.info(f'镗铣床允差值已计算并保存: {machine.name} (ID: {machine.id})')
                    
                except Exception as e:
                    logger.error(f'计算镗铣床允差值时出错: {str(e)}')
            
            # 获取机床类型显示文本
            machine_type_display = dict(Machine._meta.get_field('machine_type').choices).get(machine.machine_type, machine.machine_type)
            
            # 返回JSON响应
            return JsonResponse({
                'success': True,
                'message': '添加成功',
                'machine': {
                    'id': machine.id,
                    'name': machine.name,
                    'model': machine.model,
                    'report_number': machine.report_number,
                    'manufacturer': machine.manufacturer,
                    'created_at': machine.created_at.strftime('%Y-%m-%d'),
                    'machine_type': machine.machine_type,
                    'machine_type_display': machine_type_display,
                    'x_axis_travel': machine.x_axis_travel,
                    'y_axis_travel': machine.y_axis_travel,
                    'z_axis_travel': machine.z_axis_travel,
                    'worktable_length': machine.worktable_length,
                    'workpiece_size': machine.workpiece_size,
                    'spindle_type': machine.spindle_type,
                    'column_measurement_range': machine.column_measurement_range,
                    'worktable_x_range': machine.worktable_x_range,
                    'spindle_box_y_range': machine.spindle_box_y_range,
                    'z_axis_measurement_range': machine.z_axis_measurement_range,
                    'worktable_length_lc': machine.worktable_length_lc,
                    'boring_axis_diameter': machine.boring_axis_diameter,
                    'milling_axis_diameter': machine.milling_axis_diameter,
                    'worktable_type': machine.worktable_type
                }
            })
        except Exception as e:
            # 返回错误信息
            return JsonResponse({
                'success': False,
                'message': f'添加失败: {str(e)}'
            })
    
    # 如果不是POST请求，返回错误信息
    return JsonResponse({
        'success': False,
        'message': '无效的请求方法'
    })

@login_required
def save_machine(request, machine_id):
    """保存机床（标记为管理员已保存）"""
    from apps.evaluation.models import Machine
    from django.http import JsonResponse
    from django.utils import timezone
    
    if request.method == 'POST':
        try:
            # 获取要保存的机床
            machine = Machine.objects.get(id=machine_id)
            
            # 设置admin_saved标志为True
            machine.admin_saved = True
            machine.updated_at = timezone.now()
            machine.save()
            
            logger.info(f'机床已标记为管理员保存: {machine.name} (ID: {machine_id})')
            
            return JsonResponse({
                'success': True,
                'message': '保存成功'
            })
        except Machine.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '机床不存在'
            })
        except Exception as e:
            logger.error(f'保存机床失败: {str(e)}')
            return JsonResponse({
                'success': False,
                'message': f'保存失败: {str(e)}'
            })
    else:
        return JsonResponse({
            'success': False,
            'message': '无效的请求方法'
        })

@login_required
def delete_machine(request, machine_id):
    """删除机床及其所有相关数据"""
    from apps.evaluation.models import Machine, ComprehensiveWeightResult, UserEvaluationResult, AHPMatrix, EntropyWeight
    from apps.data_management.services.dameng_service import DamengDatabaseService
    from django.http import JsonResponse
    from django.db import connection
    
    try:
        # 获取要删除的机床
        # 使用 defer 排除可能不存在的 admin_saved 字段
        try:
            machine = Machine.objects.defer('admin_saved').get(id=machine_id)
        except Exception:
            # 如果 defer 失败，使用普通查询
            machine = Machine.objects.get(id=machine_id)
        
        logger.info(f'开始删除机床及其所有相关数据: {machine.name} (ID: {machine_id})')
        
        # 1. 删除达梦数据库中的所有相关数据
        dameng_result = DamengDatabaseService.delete_machine_data(
            machine_id, 
            request.user.username, 
            request.META.get('REMOTE_ADDR', '127.0.0.1')
        )
        if dameng_result['success']:
            logger.info(f'达梦数据库数据删除成功: {dameng_result["message"]}')
        else:
            logger.warning(f'达梦数据库数据删除失败: {dameng_result["message"]}')
        
        # 2. 删除MySQL数据库中的UserEvaluationResult记录
        try:
            user_results = UserEvaluationResult.objects.filter(machine=machine)
            if user_results.exists():
                count = user_results.count()
                user_results.delete()
                logger.info(f"删除了 {count} 条UserEvaluationResult记录")
        except Exception as user_error:
            logger.warning(f"删除UserEvaluationResult记录时出错: {str(user_error)}")
        
        # 3. 删除MySQL数据库中的ComprehensiveWeightResult记录
        try:
            comprehensive_results = ComprehensiveWeightResult.objects.filter(machine=machine)
            if comprehensive_results.exists():
                count = comprehensive_results.count()
                comprehensive_results.delete()
                logger.info(f"删除了 {count} 条ComprehensiveWeightResult记录")
        except Exception as comprehensive_error:
            logger.warning(f"删除ComprehensiveWeightResult记录时出错: {str(comprehensive_error)}")
        
        # 4. 删除MySQL数据库中的AHPMatrix记录
        try:
            ahp_matrices = AHPMatrix.objects.filter(machine=machine)
            if ahp_matrices.exists():
                count = ahp_matrices.count()
                ahp_matrices.delete()
                logger.info(f"删除了 {count} 条AHPMatrix记录")
        except Exception as ahp_error:
            logger.warning(f"删除AHPMatrix记录时出错: {str(ahp_error)}")
        
        # 5. 删除MySQL数据库中的EntropyWeight记录
        try:
            entropy_weights = EntropyWeight.objects.filter(machine=machine)
            if entropy_weights.exists():
                count = entropy_weights.count()
                entropy_weights.delete()
                logger.info(f"删除了 {count} 条EntropyWeight记录")
        except Exception as entropy_error:
            logger.warning(f"删除EntropyWeight记录时出错: {str(entropy_error)}")
        
        # 6. 使用原始SQL删除机床，绕过Django的CASCADE机制
        # 这样可以避免Django尝试删除不存在的表
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM EVALUATION_MACHINE WHERE ID = %s", [machine_id])
        
        logger.info(f'机床删除成功: {machine.name} (ID: {machine_id})')
        
        # 返回成功响应
        return JsonResponse({
            'success': True,
            'message': f'机床及其所有相关数据删除成功！'
        })
    except Machine.DoesNotExist:
        # 返回错误信息
        return JsonResponse({
            'success': False,
            'message': '机床不存在！'
        })
    except Exception as e:
        # 返回错误信息
        logger.error(f'删除机床失败: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'删除失败: {str(e)}'
        })

@login_required
def edit_machine(request, machine_id):
    """编辑机床"""
    from apps.evaluation.models import Machine
    from django.http import JsonResponse
    from django.utils import timezone
    
    if request.method == 'GET':
        try:
            # 获取要编辑的机床
            machine = Machine.objects.get(id=machine_id)
            
            # 获取机床类型显示文本
            machine_type_display = dict(Machine._meta.get_field('machine_type').choices).get(machine.machine_type, machine.machine_type)
            
            # 返回 JSON 响应
            return JsonResponse({
                'success': True,
                'machine': {
                    'id': machine.id,
                    'name': machine.name,
                    'model': machine.model,
                    'machine_number': machine.machine_number,
                    'report_number': machine.report_number,
                    'manufacturer': machine.manufacturer,
                    'production_date': machine.production_date.strftime('%Y-%m') if machine.production_date else None,
                    'created_at': machine.created_at.strftime('%Y-%m-%d'),
                    'machine_type': machine.machine_type,
                    'machine_type_display': machine_type_display,
                    # 包含加工中心参数
                    'x_axis_travel': machine.x_axis_travel,
                    'y_axis_travel': machine.y_axis_travel,
                    'z_axis_travel': machine.z_axis_travel,
                    'worktable_length': machine.worktable_length,
                    'worktable_length_lc': machine.worktable_length_lc,
                    'workpiece_size': machine.workpiece_size,
                    'spindle_type': machine.spindle_type,
                    # 包含镗铣床参数
                    'column_measurement_range': machine.column_measurement_range,
                    'worktable_x_range': machine.worktable_x_range,
                    'spindle_box_y_range': machine.spindle_box_y_range,
                    'z_axis_measurement_range': machine.z_axis_measurement_range,
                    'boring_axis_diameter': machine.boring_axis_diameter,
                    'milling_axis_diameter': machine.milling_axis_diameter,
                    'worktable_type': machine.worktable_type
                }
            })
        except Machine.DoesNotExist:
            # 返回错误信息
            return JsonResponse({
                'success': False,
                'message': '机床不存在！'
            })
        except Exception as e:
            # 返回错误信息
            return JsonResponse({
                'success': False,
                'message': f'获取机床信息失败: {str(e)}'
            })
    
    if request.method == 'POST':
        try:
            # 获取要编辑的机床
            machine = Machine.objects.get(id=machine_id)
            
            # 获取表单数据
            name = request.POST.get('name')
            model = request.POST.get('model')
            report_number = request.POST.get('report_number')
            machine_type = request.POST.get('machine_type')
            
            # 更新机床基本信息
            machine.name = name
            machine.model = model
            machine.machine_number = request.POST.get('machine_number')
            machine.report_number = report_number
            machine.manufacturer = request.POST.get('manufacturer')
            machine.production_date = parse_year_month(request.POST.get('production_date'))
            machine.machine_type = machine_type
            machine.updated_at = timezone.now()
            
            # 处理加工中心特定参数
            if machine_type == 'machining_center':
                machine.x_axis_travel = float(request.POST.get('x_axis_travel', 0)) if request.POST.get('x_axis_travel') else None
                machine.y_axis_travel = float(request.POST.get('y_axis_travel', 0)) if request.POST.get('y_axis_travel') else None
                machine.z_axis_travel = float(request.POST.get('z_axis_travel', 0)) if request.POST.get('z_axis_travel') else None
                machine.worktable_length = float(request.POST.get('worktable_length', 0)) if request.POST.get('worktable_length') else None
                machine.workpiece_size = int(request.POST.get('workpiece_size', 0)) if request.POST.get('workpiece_size') else None
                machine.spindle_type = request.POST.get('spindle_type')
            
            elif machine_type == 'boring_milling_machine':
                column_measurement_range = request.POST.get('column_measurement_range')
                if column_measurement_range:
                    machine.column_measurement_range = float(column_measurement_range)
                
                worktable_x_range = request.POST.get('worktable_x_range')
                if worktable_x_range:
                    machine.worktable_x_range = float(worktable_x_range)
                
                spindle_box_y_range = request.POST.get('spindle_box_y_range')
                if spindle_box_y_range:
                    machine.spindle_box_y_range = float(spindle_box_y_range)
                
                z_axis_measurement_range = request.POST.get('z_axis_measurement_range')
                if z_axis_measurement_range:
                    machine.z_axis_measurement_range = float(z_axis_measurement_range)
                
                worktable_length_lc = request.POST.get('worktable_length_lc')
                if worktable_length_lc:
                    machine.worktable_length_lc = float(worktable_length_lc)
                
                boring_axis_diameter = request.POST.get('boring_axis_diameter')
                if boring_axis_diameter:
                    machine.boring_axis_diameter = float(boring_axis_diameter)
                
                milling_axis_diameter = request.POST.get('milling_axis_diameter')
                if milling_axis_diameter:
                    machine.milling_axis_diameter = float(milling_axis_diameter)
                
                worktable_type = request.POST.get('worktable_type')
                if worktable_type:
                    machine.worktable_type = worktable_type
                
                machine.spindle_type = None
            
            # 保存到数据库
            machine.save()
            
            # 如果是镗铣床，计算并保存允差到 tolerance_group_1
            if machine_type == 'boring_milling_machine':
                try:
                    from apps.evaluation.views import calculate_boring_milling_tolerances
                    
                    # 计算镗铣床允差值
                    tolerances = calculate_boring_milling_tolerances(
                        machine.column_measurement_range,
                        machine.worktable_x_range,
                        machine.spindle_box_y_range
                    )
                    
                    # 添加工作台平面度允差
                    if machine.worktable_length_lc:
                        if machine.worktable_length_lc <= 1000:
                            flatness_tolerance = 0.030
                        elif machine.worktable_length_lc <= 3000:
                            flatness_tolerance = 0.040
                        elif machine.worktable_length_lc <= 4000:
                            flatness_tolerance = 0.050
                        else:
                            flatness_tolerance = 0.060
                        
                        tolerances['工作台平面度'] = {
                            '允差值': flatness_tolerance,
                            '工作台长边长度': machine.worktable_length_lc
                        }
                    
                    # 添加镗轴直径相关允差
                    if machine.boring_axis_diameter:
                        if machine.boring_axis_diameter <= 125:
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
                                '镗轴直径': machine.boring_axis_diameter
                            },
                            '镗轴的径向跳动': {
                                '允差值': spindle_runout,
                                '镗轴直径': machine.boring_axis_diameter
                            },
                            '周期性的轴向窜动': {
                                '允差值': axial_play,
                                '镗轴直径': machine.boring_axis_diameter
                            }
                        }
                    
                    # 添加铣轴直径相关允差
                    if machine.milling_axis_diameter:
                        if machine.milling_axis_diameter <= 125:
                            milling_axis_runout = 0.010
                            milling_axis_axial_play = 0.010
                        else:
                            milling_axis_runout = 0.015
                            milling_axis_axial_play = 0.015
                        
                        tolerances['铣轴直径相关'] = {
                            '铣轴端部的径向跳动': {
                                '允差值': milling_axis_runout,
                                '铣轴直径': machine.milling_axis_diameter
                            },
                            '铣轴端部的周期性轴向窜动': {
                                '允差值': milling_axis_axial_play,
                                '铣轴直径': machine.milling_axis_diameter
                            }
                        }
                    
                    # 添加工作台类型相关允差
                    if machine.worktable_type:
                        if '任意角度' in machine.worktable_type or '定位' in machine.worktable_type:
                            positioning_accuracy = 18.000
                            repeatability = 10.000
                        else:
                            positioning_accuracy = 11.000
                            repeatability = 6.000
                        
                        tolerances['工作台类型相关'] = {
                            '双向定位精度': {
                                '允差值': positioning_accuracy,
                                '工作台类型': machine.worktable_type
                            },
                            '单向重复定位精度': {
                                '允差值': repeatability,
                                '工作台类型': machine.worktable_type
                            }
                        }
                    
                    # 保存到 tolerance_group_1
                    machine.tolerance_group_1 = {
                        'boring_milling_geometric': tolerances
                    }
                    machine.save()
                    logger.info(f'镗铣床允差值已计算并保存: {machine.name} (ID: {machine.id})')
                    
                except Exception as e:
                    logger.error(f'计算镗铣床允差值时出错: {str(e)}')
            
            # 如果是管理员编辑其他用户的机床，设置admin_saved标志
            try:
                if request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin'):
                    if machine.created_by != request.user:
                        machine.admin_saved = True
                        machine.save()
            except AttributeError:
                # admin_saved 字段不存在，跳过此步骤
                logger.warning('admin_saved 字段不存在，无法设置保存状态')

            # 获取机床类型显示文本
            machine_type_display = dict(Machine._meta.get_field('machine_type').choices).get(machine.machine_type, machine.machine_type)
            
            response_data = {
                'success': True,
                'message': '编辑成功',
                'machine': {
                    'id': machine.id,
                    'name': machine.name,
                    'model': machine.model,
                    'machine_number': machine.machine_number,
                    'report_number': machine.report_number,
                    'manufacturer': machine.manufacturer,
                    'production_date': machine.production_date.strftime('%Y-%m') if machine.production_date else None,
                    'created_at': machine.created_at.strftime('%Y-%m-%d'),
                    'machine_type': machine.machine_type,
                    'machine_type_display': machine_type_display,
                    'x_axis_travel': machine.x_axis_travel,
                    'y_axis_travel': machine.y_axis_travel,
                    'z_axis_travel': machine.z_axis_travel,
                    'worktable_length': machine.worktable_length,
                    'worktable_length_lc': machine.worktable_length_lc,
                    'workpiece_size': machine.workpiece_size,
                    'spindle_type': machine.spindle_type,
                    'column_measurement_range': machine.column_measurement_range,
                    'worktable_x_range': machine.worktable_x_range,
                    'spindle_box_y_range': machine.spindle_box_y_range,
                    'z_axis_measurement_range': machine.z_axis_measurement_range,
                    'boring_axis_diameter': machine.boring_axis_diameter,
                    'milling_axis_diameter': machine.milling_axis_diameter,
                    'worktable_type': machine.worktable_type
                }
            }

            # 返回 JSON 响应
            return JsonResponse(response_data)
        except Machine.DoesNotExist:
            # 返回错误信息
            return JsonResponse({
                'success': False,
                'message': '机床不存在！'
            })
        except Exception as e:
            # 返回错误信息
            return JsonResponse({
                'success': False,
                'message': f'编辑失败: {str(e)}'
            })
    elif request.method == 'GET':
        try:
            # 获取要编辑的机床
            # 使用 defer 排除可能不存在的 admin_saved 字段
            try:
                machine = Machine.objects.defer('admin_saved').get(id=machine_id)
            except Exception:
                # 如果 defer 失败，使用普通查询
                machine = Machine.objects.get(id=machine_id)
            
            # 获取机床类型显示文本
            machine_type_display = dict(Machine._meta.get_field('machine_type').choices).get(machine.machine_type, machine.machine_type)
            
            # 返回JSON响应
            machine_data = {
                'id': machine.id,
                'name': machine.name,
                'model': machine.model,
                'report_number': machine.report_number,
                'machine_type': machine.machine_type,
                'machine_type_display': machine_type_display,
                # 包含加工中心和镗铣床参数
                'x_axis_travel': machine.x_axis_travel,
                'y_axis_travel': machine.y_axis_travel,
                'z_axis_travel': machine.z_axis_travel,
                'worktable_length': machine.worktable_length,
                'worktable_length_lc': machine.worktable_length_lc,  # 添加缺失的字段
                'workpiece_size': machine.workpiece_size,
                'spindle_type': machine.spindle_type
            }

            return JsonResponse({
                'success': True,
                'machine': machine_data
            })
        except Machine.DoesNotExist:
            # 返回错误信息
            return JsonResponse({
                'success': False,
                'message': '机床不存在！'
            })
        except Exception as e:
            # 返回错误信息
            return JsonResponse({
                'success': False,
                'message': f'获取机床信息失败: {str(e)}'
            })
    
    # 如果不是POST或GET请求，返回错误信息
    return JsonResponse({
        'success': False,
        'message': '无效的请求方法'
    })

@login_required
def fix_machine_model_report_number(request, machine_id):
    """修复机床model和report_number字段混淆的问题"""
    from django.http import JsonResponse
    try:
        machine = Machine.objects.get(id=machine_id)
        
        if request.method == 'POST':
            import json
            data = json.loads(request.body)
            correct_model = data.get('model')
            correct_report_number = data.get('report_number')
            
            if correct_model:
                machine.model = correct_model
            if correct_report_number:
                machine.report_number = correct_report_number
            
            machine.save()
            
            return JsonResponse({
                'success': True,
                'message': f'机床 {machine_id} 已修复: model={machine.model}, report_number={machine.report_number}'
            })
        
        # GET请求返回当前数据
        return JsonResponse({
            'success': True,
            'machine': {
                'id': machine.id,
                'name': machine.name,
                'current_model': machine.model,
                'current_report_number': machine.report_number
            }
        })
        
    except Machine.DoesNotExist:
        return JsonResponse({'success': False, 'message': '机床不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def create_operation_log_table(request):
    """临时API：创建 evaluation 应用的所有表"""
    from django.http import JsonResponse
    from django.db import connection
    
    results = []
    
    tables_sql = {
        'EVALUATION_MACHINE': '''
            CREATE TABLE "EVALUATION_MACHINE" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "NAME" VARCHAR(200),
                "MODEL" VARCHAR(100),
                "REPORT_NUMBER" VARCHAR(100),
                "MANUFACTURER" VARCHAR(100),
                "MACHINE_TYPE" VARCHAR(20),
                "WORKPIECE_SIZE" VARCHAR(100),
                "WORKPIECE_MATERIAL" VARCHAR(100),
                "CONTROL_SYSTEM" VARCHAR(100),
                "AXIS_COUNT" INT,
                "MAX_SPINDLE_SPEED" INT,
                "MAX_FEED_RATE" INT,
                "POWER" FLOAT,
                "WEIGHT" FLOAT,
                "DIMENSIONS" VARCHAR(100),
                "PRECISION_CLASS" VARCHAR(50),
                "MANUFACTURE_DATE" DATE,
                "PURCHASE_DATE" DATE,
                "REMARKS" TEXT,
                "CREATED_AT" TIMESTAMP,
                "UPDATED_AT" TIMESTAMP,
                "CREATED_BY_ID" INT,
                "ADMIN_SAVED" SMALLINT DEFAULT 0,
                "TOLERANCE_GROUP_1" TEXT
            )
        ''',
        'EVALUATION_EVALUATION': '''
            CREATE TABLE "EVALUATION_EVALUATION" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "MACHINE_ID" INT,
                "EVALUATOR_ID" INT,
                "EVALUATION_TYPE" VARCHAR(50),
                "STATUS" VARCHAR(20),
                "AHP_WEIGHTS" TEXT,
                "ENTROPY_WEIGHTS" TEXT,
                "COMBINED_WEIGHTS" TEXT,
                "TOTAL_SCORE" FLOAT,
                "GRADE" VARCHAR(10),
                "REMARKS" TEXT,
                "CREATED_AT" TIMESTAMP,
                "UPDATED_AT" TIMESTAMP
            )
        ''',
        'EVALUATION_AHPMATRIX': '''
            CREATE TABLE "EVALUATION_AHPMATRIX" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "MACHINE_ID" INT,
                "EVALUATOR_ID" INT,
                "MATRIX_DATA" TEXT,
                "CONSISTENCY_RATIO" FLOAT,
                "CALCULATED_AT" TIMESTAMP
            )
        ''',
        'EVALUATION_ENTROPYWEIGHT': '''
            CREATE TABLE "EVALUATION_ENTROPYWEIGHT" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "MACHINE_ID" INT,
                "EVALUATOR_ID" INT,
                "PRECISION_TYPE" VARCHAR(20) DEFAULT 'feed_axis',
                "TOTAL_ID" VARCHAR(100),
                "ENTROPY_WEIGHTS" TEXT,
                "STANDARD_VALUES" TEXT,
                "VERSION" INT DEFAULT 0,
                "UPDATED_AT" TIMESTAMP,
                "CONSTRAINT" VARCHAR(100)
            )
        ''',
        'EVALUATION_COMPREHENSIVEWEIGHTRESULT': '''
            CREATE TABLE "EVALUATION_COMPREHENSIVEWEIGHTRESULT" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "ALPHA" FLOAT DEFAULT 0.5,
                "AHP_WEIGHTS" TEXT,
                "ENTROPY_WEIGHTS" TEXT,
                "COMBINED_WEIGHTS" TEXT,
                "MEASURED_VALUES" TEXT,
                "STANDARD_VALUES" TEXT,
                "TOLERANCES" TEXT,
                "GLOBAL_WEIGHTS" TEXT,
                "INDICATOR_SCORES" TEXT,
                "WEIGHTED_SCORES" TEXT,
                "TOTAL_SCORE" FLOAT DEFAULT 0,
                "GRADE" VARCHAR(2),
                "CALCULATED_AT" TIMESTAMP,
                "NOTES" TEXT,
                "EVALUATOR_ID" INT,
                "MACHINE_ID" INT,
                "PRECISION_SCORE" FLOAT,
                "PERFORMANCE_SCORE" FLOAT,
                "RELIABILITY_SCORE" FLOAT,
                "INTELLIGENCE_SCORE" FLOAT,
                "GREEN_SCORE" FLOAT
            )
        ''',
        'EVALUATION_USEREVALUATIONRESULT': '''
            CREATE TABLE "EVALUATION_USEREVALUATIONRESULT" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "MACHINE_ID" INT,
                "EVALUATOR_ID" INT,
                "TOLERANCE_DATA" TEXT,
                "ENTROPY_WEIGHTS" TEXT,
                "STANDARD_VALUES" TEXT,
                "TOTAL_SCORE" FLOAT,
                "CREATED_AT" TIMESTAMP,
                "UPDATED_AT" TIMESTAMP
            )
        ''',
        'EVALUATION_DATAOPERATIONLOG': '''
            CREATE TABLE "EVALUATION_DATAOPERATIONLOG" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "OPERATOR_ID" INT NOT NULL,
                "ACTION" VARCHAR(10) NOT NULL,
                "TABLE_NAME" VARCHAR(100) NOT NULL,
                "RECORD_ID" VARCHAR(100) NOT NULL,
                "MACHINE_ID" INT NOT NULL,
                "OLD_DATA" TEXT,
                "NEW_DATA" TEXT,
                "IP_ADDRESS" VARCHAR(50),
                "USER_AGENT" VARCHAR(200),
                "OPERATION_TIME" TIMESTAMP,
                "NOTES" TEXT
            )
        ''',
        'EVALUATION_SYSTEMSETTINGS': '''
            CREATE TABLE "EVALUATION_SYSTEMSETTINGS" (
                "ID" INT IDENTITY(1,1) PRIMARY KEY,
                "KEY" VARCHAR(100),
                "VALUE" TEXT,
                "DESCRIPTION" TEXT,
                "CREATED_AT" TIMESTAMP,
                "UPDATED_AT" TIMESTAMP
            )
        ''',
    }
    
    try:
        with connection.cursor() as cursor:
            for table_name, sql in tables_sql.items():
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
                    cursor.execute(sql)
                    results.append(f'{table_name} ✓')
                except Exception as e:
                    results.append(f'{table_name} ✗: {str(e)[:50]}')
                        
        return JsonResponse({'success': True, 'message': '; '.join(results)})
    except Exception as e:
        import traceback
        error_msg = str(e) + '\n' + traceback.format_exc()
        print(f'创建表失败: {error_msg}')
        return JsonResponse({'success': False, 'message': str(e)})