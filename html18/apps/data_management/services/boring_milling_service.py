"""镗铣床独立数据访问服务层"""
import logging
from django.db import transaction
from ..models_dameng import BoringMillingParameters, OperationLog

logger = logging.getLogger(__name__)

BM_DECIMAL_FIELDS = [
    'column_measurement_range', 'worktable_x_range', 'spindle_box_y_range',
    'z_axis_measurement_range', 'worktable_length_lc', 'boring_axis_diameter',
    'milling_axis_diameter',
    'bm_column_linearity_yz', 'bm_column_linearity_zx',
    'bm_worktable_x_linearity_xy', 'bm_worktable_x_linearity_zx',
    'bm_spindle_box_y_linearity_yz', 'bm_spindle_box_y_linearity_xy',
    'bm_column_angle_yz', 'bm_column_angle_zx', 'bm_column_angle_xy',
    'bm_worktable_x_angle_xy', 'bm_worktable_x_angle_zx', 'bm_worktable_x_angle_yz',
    'bm_spindle_box_y_angle_yz', 'bm_spindle_box_y_angle_zx',
    'bm_worktable_x_column_perpendicularity', 'bm_spindle_box_y_worktable_x_perpendicularity',
    'bm_spindle_box_y_column_perpendicularity',
    'bm_worktable_flatness', 'bm_column_parallelism', 'bm_worktable_x_parallelism',
    'bm_boring_axis_taper_radial_near', 'bm_boring_axis_taper_radial_300mm',
    'bm_boring_axis_radial_retracted', 'bm_boring_axis_radial_extended',
    'bm_milling_axis_radial', 'bm_boring_axis_axial_retracted', 'bm_milling_axis_axial',
    'bm_linear_axis_repeatability_x', 'bm_linear_axis_repeatability_y',
    'bm_linear_axis_repeatability_z', 'bm_linear_axis_repeatability_w',
    'bm_linear_axis_positioning_accuracy_x', 'bm_linear_axis_positioning_accuracy_y',
    'bm_linear_axis_positioning_accuracy_z', 'bm_linear_axis_positioning_accuracy_w',
    'bm_linear_axis_mean_deviation_x', 'bm_linear_axis_mean_deviation_y',
    'bm_linear_axis_mean_deviation_z', 'bm_linear_axis_mean_deviation_w',
    'bm_linear_axis_system_deviation_x', 'bm_linear_axis_system_deviation_y',
    'bm_linear_axis_system_deviation_z', 'bm_linear_axis_system_deviation_w',
    'bm_linear_axis_backlash_x', 'bm_linear_axis_backlash_y',
    'bm_linear_axis_backlash_z', 'bm_linear_axis_backlash_w',
    'bm_rotary_axis_repeatability_a', 'bm_rotary_axis_repeatability_b',
    'bm_rotary_axis_repeatability_c',
    'bm_rotary_axis_positioning_accuracy_a', 'bm_rotary_axis_positioning_accuracy_b',
    'bm_rotary_axis_positioning_accuracy_c',
    'bm_rotary_axis_mean_deviation_a', 'bm_rotary_axis_mean_deviation_b',
    'bm_rotary_axis_mean_deviation_c',
    'bm_rotary_axis_system_deviation_a', 'bm_rotary_axis_system_deviation_b',
    'bm_rotary_axis_system_deviation_c',
    'bm_rotary_axis_backlash_a', 'bm_rotary_axis_backlash_b',
    'bm_rotary_axis_backlash_c',
    'bm_square_a', 'bm_square_b', 'bm_square_c', 'bm_square_d', 'bm_square_e', 'bm_square_f',
    'bm_diamond_d', 'bm_diamond_e',
    'bm_circle_f', 'bm_circle_g',
    'bm_boring_hole_h', 'bm_boring_hole_i',
    'bm_tool_magazine_positioning_accuracy', 'bm_tool_magazine_repeatability',
    # 性能模块参数 - 加工性能
    'cp_value', 'peak_speed', 'valley_speed', 'design_max_speed',
    'max_fast_speed', 'design_max_fast_speed', 'repeat_positioning_accuracy',
    'max_feed_speed', 'target_max_speed', 'repeat_positioning_accuracy_feed',
    # 性能模块参数 - 刚度
    'radial_stiffness', 'axial_stiffness', 'cutting_stiffness',
    'static_stiffness_accept', 'static_stiffness_value',
    # 性能模块参数 - 运行性能
    'max_vibration_speed', 'noise_value', 'initial_power', 'final_power',
    'current_unbalance', 'current_fluctuation',
    'voltage_fluctuation_min', 'voltage_fluctuation_max',
    'frequency_fluctuation_min', 'frequency_fluctuation_max',
    'radial_thermal_displacement', 'radial_thermal_gradient',
    'axial_thermal_displacement', 'axial_thermal_gradient',
    # 性能模块参数 - 负荷能力
    'measured_max_power', 'design_max_power', 'cutting_vibration_speed1',
    'measured_max_torque', 'design_max_torque', 'cutting_vibration_speed2',
    'actual_load_weight', 'max_design_weight', 'actual_load_velocity', 'max_design_velocity',
    'cutting_vibration_speed3', 'cutting_vibration_speed4',
    'max_cutting_width', 'tool_diameter', 'max_cutting_length', 'expected_cutting_length',
    'max_length_diameter_ratio', 'design_length_diameter_ratio',
    # 可靠性模块参数 - MTBF
    'total_run_time',
    # 可靠性模块参数 - 故障率
    'operation_time',
    # 可靠性模块参数 - 加工一致性
    'standard_deviation', 'mean_value',
    # 可靠性模块参数 - 加工精度保持性
    'original_precision', 'failure_precision', 'initial_precision',
    # 绿色化模块参数 - 资源循环与耗材
    'cutting_fluid_q', 'cutting_fluid_p', 'lubricant_l', 'lubricant_p', 'lubricant_x',
    # 绿色化模块参数 - 能源
    'est_value', 'eu_value', 'ec_value', 'n_value', 'v_value',
]

BM_STRING_FIELDS = [
    'worktable_type',
    # 性能模块参数 - 刚度
    'radial_machine_type', 'axial_machine_type',
    # 性能模块参数 - 运行性能
    'noise_machine_type', 'noise_weight',
    # 性能模块参数 - 负荷能力
    'load_machine_type', 'evaluation_scheme',
]

BM_JSON_FIELDS = [
    # 可靠性模块参数 - MTTR
    'repair_time_values',
    # 可靠性模块参数 - MTTF
    'failure_time_values',
    # 智能化模块参数
    'intelligence_checkbox_states',
    # 绿色化模块参数 - 资源循环与耗材
    'lightweight_items',
]

BM_INTEGER_FIELDS = [
    # 可靠性模块参数 - MTBF
    'fault_count',
    # 可靠性模块参数 - 故障率
    'fatal_failure', 'serious_failure', 'general_failure',
]


def _to_float(value):
    if value is not None:
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    return None


class BoringMillingService:
    """镗铣床独立数据访问服务"""

    @staticmethod
    def get_all_boring_milling_machines():
        """获取所有镗铣床参数列表"""
        try:
            machines = BoringMillingParameters.objects.order_by('machine_id')
            machine_list = []
            for m in machines:
                machine_list.append(BoringMillingService._model_to_dict(m))
            return {
                'success': True,
                'data': machine_list,
                'count': len(machine_list)
            }
        except Exception as e:
            logger.error(f"获取所有镗铣床参数失败: {str(e)}")
            return {'success': False, 'message': f'获取失败: {str(e)}', 'data': None}

    @staticmethod
    def get_boring_milling_parameters(machine_id):
        """获取镗铣床参数详情"""
        try:
            params = BoringMillingParameters.objects.filter(machine_id=machine_id).first()
            if params:
                return {
                    'success': True,
                    'data': BoringMillingService._model_to_dict(params)
                }
            else:
                return {
                    'success': False,
                    'message': f'未找到镗铣床 {machine_id} 的参数记录',
                    'data': None
                }
        except Exception as e:
            logger.error(f"获取镗铣床参数失败: {str(e)}")
            return {'success': False, 'message': f'获取镗铣床参数失败: {str(e)}', 'data': None}

    @staticmethod
    @transaction.atomic
    def update_boring_milling_parameters(machine_id, update_data, user='unknown', ip_address='127.0.0.1'):
        """创建或更新镗铣床参数，记录操作日志"""
        try:
            params = BoringMillingParameters.objects.filter(machine_id=machine_id).first()

            if not params:
                params = BoringMillingParameters(machine_id=machine_id)
                operation_type = 'CREATE'
                old_values = {}
            else:
                operation_type = 'UPDATE'
                old_values = BoringMillingService._model_to_dict(params)

            update_fields = []
            for field, value in update_data.items():
                if hasattr(params, field):
                    if value is None or (isinstance(value, str) and (value.strip() == '' or value.strip() == 'null' or value.strip() == 'undefined')):
                        setattr(params, field, None)
                    else:
                        try:
                            field_obj = params._meta.get_field(field)
                            if field_obj.get_internal_type() == 'DecimalField':
                                if value == '' or value is None:
                                    setattr(params, field, None)
                                else:
                                    from decimal import Decimal, InvalidOperation
                                    try:
                                        setattr(params, field, Decimal(str(value)))
                                    except InvalidOperation:
                                        setattr(params, field, None)
                            else:
                                setattr(params, field, value)
                        except Exception:
                            setattr(params, field, value)
                    update_fields.append(field)

            params.updated_by = user
            if operation_type == 'CREATE':
                params.created_by = user

            params.save()

            OperationLog.objects.create(
                machine_id=machine_id,
                operation_type=operation_type,
                operation_details=f"更新镗铣床参数: {', '.join(update_fields)}",
                old_values=old_values if operation_type == 'UPDATE' else None,
                new_values=update_data,
                operated_by=user,
                ip_address=ip_address
            )

            logger.info(f"成功更新镗铣床 {machine_id} 参数: {update_fields}")

            return {
                'success': True,
                'message': '更新成功',
                'data': {
                    'machine_id': params.machine_id,
                    'updated_fields': update_fields,
                    'operation_type': operation_type
                }
            }

        except Exception as e:
            logger.error(f"更新镗铣床参数失败: {str(e)}")
            return {'success': False, 'message': f'更新失败: {str(e)}', 'data': None}

    @staticmethod
    @transaction.atomic
    def delete_boring_milling_data(machine_id, user='unknown', ip_address='127.0.0.1'):
        """删除镗铣床参数及操作日志"""
        try:
            params = BoringMillingParameters.objects.filter(machine_id=machine_id)
            if params.exists():
                params.delete()
                OperationLog.objects.create(
                    machine_id=machine_id,
                    operation_type='DELETE',
                    operation_details='删除镗铣床参数',
                    operated_by=user,
                    ip_address=ip_address
                )
                
                from django.db import connection
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM EVALUATION_MACHINE WHERE ID = %s", [machine_id])
                except Exception as e:
                    logger.warning(f"同步删除机床列表失败: {str(e)}")
                
                return {'success': True, 'message': '删除成功'}
            return {'success': False, 'message': f'未找到镗铣床 {machine_id} 的参数记录'}
        except Exception as e:
            logger.error(f"删除镗铣床参数失败: {str(e)}")
            return {'success': False, 'message': f'删除失败: {str(e)}'}

    @staticmethod
    def validate_boring_milling_data(data):
        """验证镗铣床数据（数值字段、工作台类型）"""
        errors = []

        required_fields = ['column_measurement_range', 'worktable_x_range',
                           'spindle_box_y_range', 'worktable_length_lc']
        for field in required_fields:
            if field in data and data[field] is not None and data[field] != '':
                try:
                    value = float(data[field])
                    if value < 0:
                        errors.append(f"{field} 不能为负数")
                except (ValueError, TypeError):
                    errors.append(f"{field} 必须是有效的数字")

        optional_numeric_fields = ['z_axis_measurement_range', 'boring_axis_diameter',
                                   'milling_axis_diameter']
        for field in optional_numeric_fields:
            if field in data and data[field] is not None and data[field] != '':
                try:
                    value = float(data[field])
                    if value < 0:
                        errors.append(f"{field} 不能为负数")
                except (ValueError, TypeError):
                    errors.append(f"{field} 必须是有效的数字")

        if not errors:
            return True, []
        return False, errors

    @staticmethod
    def clear_all_data():
        """清空所有镗铣床参数数据（谨慎使用）"""
        try:
            count = BoringMillingParameters.objects.count()
            BoringMillingParameters.objects.all().delete()
            logger.info(f"已清空所有镗铣床参数数据，共删除 {count} 条记录")
            return {'success': True, 'message': f'已清空 {count} 条记录'}
        except Exception as e:
            logger.error(f"清空镗铣床参数失败: {str(e)}")
            return {'success': False, 'message': f'清空失败: {str(e)}'}

    @staticmethod
    def _model_to_dict(m):
        """将BoringMillingParameters模型实例转换为字典"""
        result = {
            'machine_id': m.machine_id,
            'machine_type': 'boring_milling_machine',
        }

        for field in BM_DECIMAL_FIELDS:
            result[field] = _to_float(getattr(m, field, None))

        for field in BM_STRING_FIELDS:
            result[field] = getattr(m, field, None)

        for field in BM_JSON_FIELDS:
            result[field] = getattr(m, field, None)

        for field in BM_INTEGER_FIELDS:
            result[field] = getattr(m, field, None)

        result['updated_at'] = m.updated_at.strftime('%Y-%m-%d %H:%M:%S') if m.updated_at else None

        return result
