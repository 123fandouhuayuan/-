"""达梦数据库服务层"""
import logging
from django.db import transaction
from ..models_dameng import MachineParameters, OperationLog, BoringMillingParameters

logger = logging.getLogger(__name__)


class DamengDatabaseService:
    """达梦数据库服务类"""
    
    @staticmethod
    def get_all_machines():
        """获取所有加工中心机床参数列表"""
        try:
            machines = MachineParameters.objects.order_by('machine_id')
            machine_list = []
            for machine in machines:
                machine_list.append({
                    'machine_id': machine.machine_id,
                    'machine_type': machine.machine_type,
                    'x_axis_travel': float(machine.x_axis_travel) if machine.x_axis_travel else None,
                    'y_axis_travel': float(machine.y_axis_travel) if machine.y_axis_travel else None,
                    'z_axis_travel': float(machine.z_axis_travel) if machine.z_axis_travel else None,
                    'worktable_length': float(machine.worktable_length) if machine.worktable_length else None,
                    'workpiece_size': machine.workpiece_size,
                    'spindle_type': machine.spindle_type
                })
            return {
                'success': True,
                'data': machine_list,
                'count': len(machine_list)
            }
        except Exception as e:
            logger.error(f"获取所有机床参数失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_machine_parameters(machine_id):
        """获取加工中心机床参数详情（包含所有精度检测项）"""
        try:
            params = MachineParameters.objects.filter(machine_id=machine_id).first()
            if params:
                return {
                    'success': True,
                    'data': {
                        'machine_id': params.machine_id,
                        'machine_type': params.machine_type,
                        'x_axis_travel': float(params.x_axis_travel) if params.x_axis_travel else None,
                        'y_axis_travel': float(params.y_axis_travel) if params.y_axis_travel else None,
                        'z_axis_travel': float(params.z_axis_travel) if params.z_axis_travel else None,
                        'worktable_length': float(params.worktable_length) if params.worktable_length else None,
                        'workpiece_size': params.workpiece_size,
                        'spindle_type': params.spindle_type,
                        # 直线度检测项目
                        'x_axis_linearity_xy': float(params.x_axis_linearity_xy) if params.x_axis_linearity_xy is not None else None,
                        'x_axis_linearity_zx': float(params.x_axis_linearity_zx) if params.x_axis_linearity_zx is not None else None,
                        'z_axis_linearity_yz': float(params.z_axis_linearity_yz) if params.z_axis_linearity_yz is not None else None,
                        'z_axis_linearity_zx': float(params.z_axis_linearity_zx) if params.z_axis_linearity_zx is not None else None,
                        'y_axis_linearity_xy': float(params.y_axis_linearity_xy) if params.y_axis_linearity_xy is not None else None,
                        'y_axis_linearity_yz': float(params.y_axis_linearity_yz) if params.y_axis_linearity_yz is not None else None,
                        # 角度偏差检测项目
                        'x_axis_angle_pitch': float(params.x_axis_angle_pitch) if params.x_axis_angle_pitch is not None else None,
                        'x_axis_angle_yaw': float(params.x_axis_angle_yaw) if params.x_axis_angle_yaw is not None else None,
                        'x_axis_angle_roll': float(params.x_axis_angle_roll) if params.x_axis_angle_roll is not None else None,
                        'z_axis_angle_pitch': float(params.z_axis_angle_pitch) if params.z_axis_angle_pitch is not None else None,
                        'z_axis_angle_yaw': float(params.z_axis_angle_yaw) if params.z_axis_angle_yaw is not None else None,
                        'z_axis_angle_roll': float(params.z_axis_angle_roll) if params.z_axis_angle_roll is not None else None,
                        'y_axis_angle_yz': float(params.y_axis_angle_yz) if params.y_axis_angle_yz is not None else None,
                        'y_axis_angle_xy': float(params.y_axis_angle_xy) if params.y_axis_angle_xy is not None else None,
                        'y_axis_angle_zx': float(params.y_axis_angle_zx) if params.y_axis_angle_zx is not None else None,
                        # 垂直度检测项目
                        'y_axis_perpendicularity_x': float(params.y_axis_perpendicularity_x) if params.y_axis_perpendicularity_x is not None else None,
                        'y_axis_perpendicularity_z': float(params.y_axis_perpendicularity_z) if params.y_axis_perpendicularity_z is not None else None,
                        'z_axis_perpendicularity_x': float(params.z_axis_perpendicularity_x) if params.z_axis_perpendicularity_x is not None else None,
                        # 主轴精度检测项目
                        'spindle_axial_runout': float(params.spindle_axial_runout) if params.spindle_axial_runout is not None else None,
                        'spindle_radial_runout_near': float(params.spindle_radial_runout_near) if params.spindle_radial_runout_near is not None else None,
                        'spindle_radial_runout_300mm': float(params.spindle_radial_runout_300mm) if params.spindle_radial_runout_300mm is not None else None,
                        'spindle_parallelism_yz': float(params.spindle_parallelism_yz) if params.spindle_parallelism_yz is not None else None,
                        'spindle_parallelism_zx': float(params.spindle_parallelism_zx) if params.spindle_parallelism_zx is not None else None,
                        'spindle_perpendicularity_x': float(params.spindle_perpendicularity_x) if params.spindle_perpendicularity_x is not None else None,
                        'spindle_perpendicularity_y': float(params.spindle_perpendicularity_y) if params.spindle_perpendicularity_y is not None else None,
                        # 工作台精度检测项目
                        'worktable_flatness': float(params.worktable_flatness) if params.worktable_flatness is not None else None,
                        'worktable_parallelism_x': float(params.worktable_parallelism_x) if params.worktable_parallelism_x is not None else None,
                        'worktable_parallelism_z': float(params.worktable_parallelism_z) if params.worktable_parallelism_z is not None else None,
                        # 位置精度检测项目 - 线性轴
                        'linear_axis_repeatability_x': float(params.linear_axis_repeatability_x) if params.linear_axis_repeatability_x is not None else None,
                        'linear_axis_repeatability_y': float(params.linear_axis_repeatability_y) if params.linear_axis_repeatability_y is not None else None,
                        'linear_axis_repeatability_z': float(params.linear_axis_repeatability_z) if params.linear_axis_repeatability_z is not None else None,
                        'linear_axis_positioning_accuracy_x': float(params.linear_axis_positioning_accuracy_x) if params.linear_axis_positioning_accuracy_x is not None else None,
                        'linear_axis_positioning_accuracy_y': float(params.linear_axis_positioning_accuracy_y) if params.linear_axis_positioning_accuracy_y is not None else None,
                        'linear_axis_positioning_accuracy_z': float(params.linear_axis_positioning_accuracy_z) if params.linear_axis_positioning_accuracy_z is not None else None,
                        'linear_axis_mean_deviation_x': float(params.linear_axis_mean_deviation_x) if params.linear_axis_mean_deviation_x is not None else None,
                        'linear_axis_mean_deviation_y': float(params.linear_axis_mean_deviation_y) if params.linear_axis_mean_deviation_y is not None else None,
                        'linear_axis_mean_deviation_z': float(params.linear_axis_mean_deviation_z) if params.linear_axis_mean_deviation_z is not None else None,
                        'linear_axis_system_deviation_x': float(params.linear_axis_system_deviation_x) if params.linear_axis_system_deviation_x is not None else None,
                        'linear_axis_system_deviation_y': float(params.linear_axis_system_deviation_y) if params.linear_axis_system_deviation_y is not None else None,
                        'linear_axis_system_deviation_z': float(params.linear_axis_system_deviation_z) if params.linear_axis_system_deviation_z is not None else None,
                        'linear_axis_backlash_x': float(params.linear_axis_backlash_x) if params.linear_axis_backlash_x is not None else None,
                        'linear_axis_backlash_y': float(params.linear_axis_backlash_y) if params.linear_axis_backlash_y is not None else None,
                        'linear_axis_backlash_z': float(params.linear_axis_backlash_z) if params.linear_axis_backlash_z is not None else None,
                        # 位置精度检测项目 - 回转轴
                        'rotary_axis_repeatability_a': float(params.rotary_axis_repeatability_a) if params.rotary_axis_repeatability_a is not None else None,
                        'rotary_axis_repeatability_b': float(params.rotary_axis_repeatability_b) if params.rotary_axis_repeatability_b is not None else None,
                        'rotary_axis_repeatability_c': float(params.rotary_axis_repeatability_c) if params.rotary_axis_repeatability_c is not None else None,
                        'rotary_axis_positioning_accuracy_a': float(params.rotary_axis_positioning_accuracy_a) if params.rotary_axis_positioning_accuracy_a is not None else None,
                        'rotary_axis_positioning_accuracy_b': float(params.rotary_axis_positioning_accuracy_b) if params.rotary_axis_positioning_accuracy_b is not None else None,
                        'rotary_axis_positioning_accuracy_c': float(params.rotary_axis_positioning_accuracy_c) if params.rotary_axis_positioning_accuracy_c is not None else None,
                        'rotary_axis_mean_deviation_a': float(params.rotary_axis_mean_deviation_a) if params.rotary_axis_mean_deviation_a is not None else None,
                        'rotary_axis_mean_deviation_b': float(params.rotary_axis_mean_deviation_b) if params.rotary_axis_mean_deviation_b is not None else None,
                        'rotary_axis_mean_deviation_c': float(params.rotary_axis_mean_deviation_c) if params.rotary_axis_mean_deviation_c is not None else None,
                        'rotary_axis_system_deviation_a': float(params.rotary_axis_system_deviation_a) if params.rotary_axis_system_deviation_a is not None else None,
                        'rotary_axis_system_deviation_b': float(params.rotary_axis_system_deviation_b) if params.rotary_axis_system_deviation_b is not None else None,
                        'rotary_axis_system_deviation_c': float(params.rotary_axis_system_deviation_c) if params.rotary_axis_system_deviation_c is not None else None,
                        'rotary_axis_backlash_a': float(params.rotary_axis_backlash_a) if params.rotary_axis_backlash_a is not None else None,
                        'rotary_axis_backlash_b': float(params.rotary_axis_backlash_b) if params.rotary_axis_backlash_b is not None else None,
                        'rotary_axis_backlash_c': float(params.rotary_axis_backlash_c) if params.rotary_axis_backlash_c is not None else None,
                        # 几何精度检测项目（Sheet4）
                        'cylindricity': float(params.cylindricity) if params.cylindricity is not None else None,
                        'hole_perpendicularity_a': float(params.hole_perpendicularity_a) if params.hole_perpendicularity_a is not None else None,
                        'side_linearity': float(params.side_linearity) if params.side_linearity is not None else None,
                        'adjacent_perpendicularity_b': float(params.adjacent_perpendicularity_b) if params.adjacent_perpendicularity_b is not None else None,
                        'opposite_parallelism_b': float(params.opposite_parallelism_b) if params.opposite_parallelism_b is not None else None,
                        'side_linearity_2': float(params.side_linearity_2) if params.side_linearity_2 is not None else None,
                        'side_inclination_b': float(params.side_inclination_b) if params.side_inclination_b is not None else None,
                        'circularity': float(params.circularity) if params.circularity is not None else None,
                        'concentricity_c': float(params.concentricity_c) if params.concentricity_c is not None else None,
                        'slope_linearity': float(params.slope_linearity) if params.slope_linearity is not None else None,
                        'slope_inclination_b': float(params.slope_inclination_b) if params.slope_inclination_b is not None else None,
                        'hole_position_c': float(params.hole_position_c) if params.hole_position_c is not None else None,
                        'concentricity_d': float(params.concentricity_d) if params.concentricity_d is not None else None,
                        # 加工性能参数
                        'cp_value': float(params.cp_value) if params.cp_value is not None else None,
                        'peak_speed': float(params.peak_speed) if params.peak_speed is not None else None,
                        'valley_speed': float(params.valley_speed) if params.valley_speed is not None else None,
                        'design_max_speed': float(params.design_max_speed) if params.design_max_speed is not None else None,
                        'max_fast_speed': float(params.max_fast_speed) if params.max_fast_speed is not None else None,
                        'design_max_fast_speed': float(params.design_max_fast_speed) if params.design_max_fast_speed is not None else None,
                        'repeat_positioning_accuracy': float(params.repeat_positioning_accuracy) if params.repeat_positioning_accuracy is not None else None,
                        'max_feed_speed': float(params.max_feed_speed) if params.max_feed_speed is not None else None,
                        'target_max_speed': float(params.target_max_speed) if params.target_max_speed is not None else None,
                        'repeat_positioning_accuracy_feed': float(params.repeat_positioning_accuracy_feed) if params.repeat_positioning_accuracy_feed is not None else None,
                        # 刚度参数
                        'radial_stiffness': float(params.radial_stiffness) if params.radial_stiffness is not None else None,
                        'axial_stiffness': float(params.axial_stiffness) if params.axial_stiffness is not None else None,
                        'radial_machine_type': params.radial_machine_type,
                        'axial_machine_type': params.axial_machine_type,
                        'cutting_stiffness': float(params.cutting_stiffness) if params.cutting_stiffness is not None else None,
                        'static_stiffness_accept': float(params.static_stiffness_accept) if params.static_stiffness_accept is not None else None,
                        'static_stiffness_value': float(params.static_stiffness_value) if params.static_stiffness_value is not None else None,
                        # 运行性能参数
                        'max_vibration_speed': float(params.max_vibration_speed) if params.max_vibration_speed is not None else None,
                        'noise_value': float(params.noise_value) if params.noise_value is not None else None,
                        'noise_machine_type': params.noise_machine_type,
                        'noise_weight': params.noise_weight,
                        'initial_power': float(params.initial_power) if params.initial_power is not None else None,
                        'final_power': float(params.final_power) if params.final_power is not None else None,
                        'current_unbalance': float(params.current_unbalance) if params.current_unbalance is not None else None,
                        'current_fluctuation': float(params.current_fluctuation) if params.current_fluctuation is not None else None,
                        'voltage_fluctuation_min': float(params.voltage_fluctuation_min) if params.voltage_fluctuation_min is not None else None,
                        'voltage_fluctuation_max': float(params.voltage_fluctuation_max) if params.voltage_fluctuation_max is not None else None,
                        'frequency_fluctuation_min': float(params.frequency_fluctuation_min) if params.frequency_fluctuation_min is not None else None,
                        'frequency_fluctuation_max': float(params.frequency_fluctuation_max) if params.frequency_fluctuation_max is not None else None,
                        'radial_thermal_displacement': float(params.radial_thermal_displacement) if params.radial_thermal_displacement is not None else None,
                        'radial_thermal_gradient': float(params.radial_thermal_gradient) if params.radial_thermal_gradient is not None else None,
                        'axial_thermal_displacement': float(params.axial_thermal_displacement) if params.axial_thermal_displacement is not None else None,
                        'axial_thermal_gradient': float(params.axial_thermal_gradient) if params.axial_thermal_gradient is not None else None,
                        # 负荷能力参数
                        'measured_max_power': float(params.measured_max_power) if params.measured_max_power is not None else None,
                        'design_max_power': float(params.design_max_power) if params.design_max_power is not None else None,
                        'cutting_vibration_speed1': float(params.cutting_vibration_speed1) if params.cutting_vibration_speed1 is not None else None,
                        'measured_max_torque': float(params.measured_max_torque) if params.measured_max_torque is not None else None,
                        'design_max_torque': float(params.design_max_torque) if params.design_max_torque is not None else None,
                        'cutting_vibration_speed2': float(params.cutting_vibration_speed2) if params.cutting_vibration_speed2 is not None else None,
                        'actual_load_weight': float(params.actual_load_weight) if params.actual_load_weight is not None else None,
                        'max_design_weight': float(params.max_design_weight) if params.max_design_weight is not None else None,
                        'actual_load_velocity': float(params.actual_load_velocity) if params.actual_load_velocity is not None else None,
                        'max_design_velocity': float(params.max_design_velocity) if params.max_design_velocity is not None else None,
                        'cutting_vibration_speed3': float(params.cutting_vibration_speed3) if params.cutting_vibration_speed3 is not None else None,
                        'cutting_vibration_speed4': float(params.cutting_vibration_speed4) if params.cutting_vibration_speed4 is not None else None,
                        'load_machine_type': params.load_machine_type,
                        'evaluation_scheme': params.evaluation_scheme,
                        'max_cutting_width': float(params.max_cutting_width) if params.max_cutting_width is not None else None,
                        'tool_diameter': float(params.tool_diameter) if params.tool_diameter is not None else None,
                        'max_cutting_length': float(params.max_cutting_length) if params.max_cutting_length is not None else None,
                        'expected_cutting_length': float(params.expected_cutting_length) if params.expected_cutting_length is not None else None,
                        'max_length_diameter_ratio': float(params.max_length_diameter_ratio) if params.max_length_diameter_ratio is not None else None,
                        'design_length_diameter_ratio': float(params.design_length_diameter_ratio) if params.design_length_diameter_ratio is not None else None,
                        # 可靠性模块参数 - MTBF
                        'total_run_time': float(params.total_run_time) if params.total_run_time is not None else None,
                        'fault_count': params.fault_count,
                        # 可靠性模块参数 - MTTR
                        'repair_time_values': params.repair_time_values,
                        # 可靠性模块参数 - 故障率
                        'fatal_failure': params.fatal_failure,
                        'serious_failure': params.serious_failure,
                        'general_failure': params.general_failure,
                        'operation_time': float(params.operation_time) if params.operation_time is not None else None,
                        # 可靠性模块参数 - 加工一致性
                        'standard_deviation': float(params.standard_deviation) if params.standard_deviation is not None else None,
                        'mean_value': float(params.mean_value) if params.mean_value is not None else None,
                        # 可靠性模块参数 - 加工精度保持性
                        'original_precision': float(params.original_precision) if params.original_precision is not None else None,
                        'failure_precision': float(params.failure_precision) if params.failure_precision is not None else None,
                        'initial_precision': float(params.initial_precision) if params.initial_precision is not None else None,
                        # 可靠性模块参数 - MTTF
                        'failure_time_values': params.failure_time_values,
                        # 智能化模块参数
                        'intelligence_checkbox_states': params.intelligence_checkbox_states,
                        # 绿色化模块参数 - 资源循环与耗材
                        'cutting_fluid_q': float(params.cutting_fluid_q) if params.cutting_fluid_q is not None else None,
                        'cutting_fluid_p': float(params.cutting_fluid_p) if params.cutting_fluid_p is not None else None,
                        'lubricant_l': float(params.lubricant_l) if params.lubricant_l is not None else None,
                        'lubricant_p': float(params.lubricant_p) if params.lubricant_p is not None else None,
                        'lubricant_x': float(params.lubricant_x) if params.lubricant_x is not None else None,
                        'lightweight_items': params.lightweight_items,
                        # 绿色化模块参数 - 能源
                        'est_value': float(params.est_value) if params.est_value is not None else None,
                        'eu_value': float(params.eu_value) if params.eu_value is not None else None,
                        'ec_value': float(params.ec_value) if params.ec_value is not None else None,
                        'n_value': float(params.n_value) if params.n_value is not None else None,
                        'v_value': float(params.v_value) if params.v_value is not None else None,
                        'updated_at': params.updated_at.strftime('%Y-%m-%d %H:%M:%S') if params.updated_at else None
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'未找到机床 {machine_id} 的参数记录',
                    'data': None
                }
        except Exception as e:
            logger.error(f"获取机床参数失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取机床参数失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def update_machine_parameters(machine_id, update_data, user='unknown', ip_address='127.0.0.1'):
        """创建或更新加工中心机床参数，记录操作日志"""
        try:
            params = MachineParameters.objects.filter(machine_id=machine_id).first()
            
            if not params:
                # 创建新记录
                params = MachineParameters(machine_id=machine_id)
                if 'machine_type' in update_data:
                    params.machine_type = update_data['machine_type']
                operation_type = 'CREATE'
                old_values = {}
            else:
                operation_type = 'UPDATE'
                old_values = {
                    'x_axis_travel': float(params.x_axis_travel) if params.x_axis_travel else None,
                    'y_axis_travel': float(params.y_axis_travel) if params.y_axis_travel else None,
                    'z_axis_travel': float(params.z_axis_travel) if params.z_axis_travel else None,
                    'worktable_length': float(params.worktable_length) if params.worktable_length else None,
                    'workpiece_size': params.workpiece_size,
                    'spindle_type': params.spindle_type
                }
            
            # 更新字段
            update_fields = []
            for field, value in update_data.items():
                if hasattr(params, field):
                    # 处理空值：如果值为None、空字符串或'null'，设置为None
                    if value is None or (isinstance(value, str) and (value.strip() == '' or value.strip() == 'null' or value.strip() == 'undefined')):
                        setattr(params, field, None)
                    else:
                        # 对于数值字段，确保转换为适当类型
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
            
            # 设置更新信息
            params.updated_by = user
            if operation_type == 'CREATE':
                params.created_by = user
            
            params.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                machine_id=machine_id,
                operation_type=operation_type,
                operation_details=f"更新机床参数: {', '.join(update_fields)}",
                old_values=old_values if operation_type == 'UPDATE' else None,
                new_values=update_data,
                operated_by=user,
                ip_address=ip_address
            )
            
            logger.info(f"成功更新机床 {machine_id} 参数: {update_fields}")
            
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
            logger.error(f"更新机床参数失败: {str(e)}")
            return {
                'success': False,
                'message': f'更新失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
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
                old_values = {
                    'column_measurement_range': float(params.column_measurement_range) if params.column_measurement_range else None,
                    'worktable_x_range': float(params.worktable_x_range) if params.worktable_x_range else None,
                    'spindle_box_y_range': float(params.spindle_box_y_range) if params.spindle_box_y_range else None,
                    'z_axis_measurement_range': float(params.z_axis_measurement_range) if params.z_axis_measurement_range else None,
                    'worktable_length_lc': float(params.worktable_length_lc) if params.worktable_length_lc else None,
                    'boring_axis_diameter': float(params.boring_axis_diameter) if params.boring_axis_diameter else None,
                    'milling_axis_diameter': float(params.milling_axis_diameter) if params.milling_axis_diameter else None,
                    'worktable_type': params.worktable_type,
                }
            
            update_fields = []
            for field, value in update_data.items():
                if hasattr(params, field):
                    if value is None or (isinstance(value, str) and value.strip() == ''):
                        setattr(params, field, None)
                    else:
                        setattr(params, field, value)
                    update_fields.append(field)
            
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
            return {
                'success': False,
                'message': f'更新失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_operation_logs(machine_id=None, limit=100):
        """获取操作日志，可按机床ID筛选"""
        try:
            query = OperationLog.objects.all()
            if machine_id:
                query = query.filter(machine_id=machine_id)
            
            logs = query.order_by('-operated_at')[:limit]
            
            log_data = []
            for log in logs:
                log_data.append({
                    'id': log.id,
                    'machine_id': log.machine_id,
                    'operation_type': log.operation_type,
                    'operation_details': log.operation_details,
                    'old_values': log.old_values,
                    'new_values': log.new_values,
                    'operated_by': log.operated_by,
                    'operated_at': log.operated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'ip_address': log.ip_address
                })
            
            return {
                'success': True,
                'data': log_data,
                'total': len(log_data)
            }
            
        except Exception as e:
            logger.error(f"获取操作日志失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取操作日志失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    @transaction.atomic
    def delete_machine_data(machine_id, user='unknown', ip_address='127.0.0.1'):
        """删除机床及其所有相关数据（参数、日志、权重结果）"""
        try:
            deleted_items = []
            
            # 1. 删除机床参数（加工中心）
            machine_params = MachineParameters.objects.filter(machine_id=machine_id)
            if machine_params.exists():
                count = machine_params.count()
                machine_params.delete()
                deleted_items.append(f'机床参数 ({count}条)')
                logger.info(f"删除机床参数: machine_id={machine_id}, count={count}")
            
            # 1.1 删除镗铣床参数
            from ..models_dameng import BoringMillingParameters
            boring_milling_params = BoringMillingParameters.objects.filter(machine_id=machine_id)
            if boring_milling_params.exists():
                count = boring_milling_params.count()
                boring_milling_params.delete()
                deleted_items.append(f'镗铣床参数 ({count}条)')
                logger.info(f"删除镗铣床参数: machine_id={machine_id}, count={count}")
            
            # 2. 删除综合权重结果
            from ..models_dameng import ComprehensiveWeightResultDameng
            comprehensive_weights = ComprehensiveWeightResultDameng.objects.filter(machine_id=machine_id)
            if comprehensive_weights.exists():
                count = comprehensive_weights.count()
                comprehensive_weights.delete()
                deleted_items.append(f'综合权重结果 ({count}条)')
                logger.info(f"删除综合权重结果: machine_id={machine_id}, count={count}")
            
            # 3. 删除操作日志
            operation_logs = OperationLog.objects.filter(machine_id=machine_id)
            if operation_logs.exists():
                count = operation_logs.count()
                operation_logs.delete()
                deleted_items.append(f'操作日志 ({count}条)')
                logger.info(f"删除操作日志: machine_id={machine_id}, count={count}")
            
            # 记录删除操作日志
            OperationLog.objects.create(
                machine_id=0,
                operation_type='DELETE',
                operation_details=f"删除机床及其所有相关数据: {', '.join(deleted_items)}",
                old_values={'machine_id': machine_id},
                new_values=None,
                operated_by=user,
                ip_address=ip_address
            )
            
            logger.info(f"成功删除机床 {machine_id} 的所有数据: {', '.join(deleted_items)}")
            
            return {
                'success': True,
                'message': f'删除成功: {", ".join(deleted_items)}',
                'data': {
                    'machine_id': machine_id,
                    'deleted_items': deleted_items
                }
            }
            
        except Exception as e:
            logger.error(f"删除机床数据失败: {str(e)}")
            return {
                'success': False,
                'message': f'删除失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def validate_machine_data(data):
        """验证机床数据（数值字段、工件尺寸、主轴类型、工作台类型）"""
        errors = []
        
        # 验证数值字段
        numeric_fields = ['x_axis_travel', 'y_axis_travel', 'z_axis_travel', 'worktable_length']
        for field in numeric_fields:
            if field in data and data[field] is not None and data[field] != '':
                try:
                    value = float(data[field])
                    if value < 0:
                        errors.append(f"{field} 不能为负数")
                except (ValueError, TypeError):
                    errors.append(f"{field} 必须是有效的数字")
        
        # 验证镗铣床数值字段
        boring_milling_numeric_fields = ['column_measurement_range', 'worktable_x_range', 'spindle_box_y_range', 
                                         'z_axis_measurement_range', 'worktable_length_lc', 'boring_axis_diameter', 
                                         'milling_axis_diameter']
        for field in boring_milling_numeric_fields:
            if field in data and data[field] is not None and data[field] != '':
                try:
                    value = float(data[field])
                    if value < 0:
                        errors.append(f"{field} 不能为负数")
                except (ValueError, TypeError):
                    errors.append(f"{field} 必须是有效的数字")
        
        # 验证工件尺寸
        if 'workpiece_size' in data and data['workpiece_size'] is not None and data['workpiece_size'] != '':
            try:
                value = int(data['workpiece_size'])
                if value not in [80, 160, 320]:
                    errors.append("工件尺寸必须是 80, 160 或 320")
            except (ValueError, TypeError):
                errors.append("工件尺寸必须是有效的整数")
        
        # 验证主轴类型
        valid_spindle_types = ['integral', 'attached', 'belt_driven', 'gear_driven']
        if 'spindle_type' in data and data['spindle_type'] and data['spindle_type'] not in valid_spindle_types:
            errors.append(f"主轴类型必须是以下值之一: {', '.join(valid_spindle_types)}")
        
        # 验证工作台类型
        valid_worktable_types = ['fixed_indexing', 'arbitrary_positioning']
        if 'worktable_type' in data and data['worktable_type'] and data['worktable_type'] not in valid_worktable_types:
            errors.append(f"工作台类型必须是以下值之一: {', '.join(valid_worktable_types)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def save_entropy_weight_result(machine_type, precision_type, data, user='unknown', ip_address='127.0.0.1'):
        """保存信息熵权重计算结果"""
        from ..models_dameng import EntropyWeightDameng
        from datetime import datetime
        
        try:
            if not machine_type:
                return {
                    'success': False,
                    'message': '机床类型不能为空',
                    'data': None
                }
            
            if not precision_type:
                return {
                    'success': False,
                    'message': '精度数据类型不能为空',
                    'data': None
                }
            
            valid_machine_types = [choice[0] for choice in EntropyWeightDameng.MACHINE_TYPE_CHOICES]
            if machine_type not in valid_machine_types:
                return {
                    'success': False,
                    'message': f'机床类型必须是以下值之一: {", ".join(valid_machine_types)}',
                    'data': None
                }
            
            valid_precision_types = [choice[0] for choice in EntropyWeightDameng.PRECISION_TYPE_CHOICES]
            if precision_type not in valid_precision_types:
                return {
                    'success': False,
                    'message': f'精度数据类型必须是以下值之一: {", ".join(valid_precision_types)}',
                    'data': None
                }
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            total_id = f"ENTROPY_{machine_type}_{precision_type}_{timestamp}"
            
            sample_count = data.get('sample_count', 0)
            indicator_names = data.get('indicator_names', [])
            input_data = data.get('input_data', [])
            entropy_values = data.get('entropy_values', [])
            weights = data.get('weights', [])
            tolerance_values = data.get('tolerance_values')
            standard_values = data.get('standard_values')
            description = data.get('description', '')
            
            with transaction.atomic():
                existing_record = EntropyWeightDameng.objects.filter(
                    machine_type=machine_type,
                    precision_type=precision_type
                ).first()
                
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
                    existing_record.evaluator = user
                    existing_record.version += 1
                    existing_record.save()
                    
                    record = existing_record
                    operation_type = 'UPDATE'
                else:
                    record = EntropyWeightDameng.objects.create(
                        machine_type=machine_type,
                        precision_type=precision_type,
                        total_id=total_id,
                        sample_count=sample_count,
                        indicator_names=indicator_names,
                        input_data=input_data,
                        entropy_values=entropy_values,
                        weights=weights,
                        tolerance_values=tolerance_values,
                        standard_values=standard_values,
                        description=description,
                        evaluator=user
                    )
                    operation_type = 'CREATE'
                
                OperationLog.objects.create(
                    machine_id=0,
                    operation_type=operation_type,
                    operation_details=f"保存信息熵权重计算结果: {machine_type} - {precision_type}",
                    new_values={
                        'total_id': total_id,
                        'machine_type': machine_type,
                        'precision_type': precision_type,
                        'sample_count': sample_count,
                        'indicator_names': indicator_names
                    },
                    operated_by=user,
                    ip_address=ip_address
                )
            
            logger.info(f"成功保存信息熵权重计算结果: {machine_type}, 类型{precision_type}")
            
            return {
                'success': True,
                'message': '保存成功',
                'data': {
                    'id': record.id,
                    'total_id': total_id,
                    'machine_type': machine_type,
                    'precision_type': precision_type,
                    'operation_type': operation_type
                }
            }
            
        except Exception as e:
            logger.error(f"保存信息熵权重计算结果失败: {str(e)}")
            return {
                'success': False,
                'message': f'保存失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_entropy_weight_result(machine_type, precision_type=None):
        """获取信息熵权重计算结果，可按精度类型筛选"""
        from ..models_dameng import EntropyWeightDameng
        
        try:
            if not machine_type:
                return {
                    'success': False,
                    'message': '机床类型不能为空',
                    'data': None
                }
            
            query = EntropyWeightDameng.objects.filter(machine_type=machine_type)
            
            if precision_type:
                query = query.filter(precision_type=precision_type)
            
            results = query.order_by('-calculated_at')
            
            data_list = []
            for result in results:
                data_list.append({
                    'id': result.id,
                    'machine_type': result.machine_type,
                    'machine_type_display': result.get_machine_type_display(),
                    'precision_type': result.precision_type,
                    'precision_type_display': result.get_precision_type_display(),
                    'total_id': result.total_id,
                    'sample_count': result.sample_count,
                    'indicator_names': result.indicator_names,
                    'input_data': result.input_data,
                    'entropy_values': result.entropy_values,
                    'weights': result.weights,
                    'tolerance_values': result.tolerance_values,
                    'standard_values': result.standard_values,
                    'description': result.description,
                    'evaluator': result.evaluator,
                    'calculated_at': result.calculated_at.strftime('%Y-%m-%d %H:%M:%S') if result.calculated_at else None,
                    'updated_at': result.updated_at.strftime('%Y-%m-%d %H:%M:%S') if result.updated_at else None,
                    'version': result.version
                })
            
            return {
                'success': True,
                'data': data_list if not precision_type else (data_list[0] if data_list else None),
                'count': len(data_list)
            }
            
        except Exception as e:
            logger.error(f"获取信息熵权重计算结果失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    @transaction.atomic
    def save_comprehensive_weight_result(machine_type, report_number, machine_id, machine_model, comprehensive_score, total_weight, 
                                        precision_score=0, performance_score=0, reliability_score=0, 
                                        intelligence_score=0, green_score=0, user='unknown', ip_address='127.0.0.1'):
        """保存综合权重计算结果（每台机床仅保留一条记录，以报告编号为基准）"""
        from ..models_dameng import ComprehensiveWeightResultDameng
        from datetime import datetime
        
        try:
            
            if not machine_type:
                return {
                    'success': False,
                    'message': '机床类型不能为空',
                    'data': None
                }
            
            if not report_number:
                return {
                    'success': False,
                    'message': '报告编号不能为空',
                    'data': None
                }
            
            if machine_id is None:
                return {
                    'success': False,
                    'message': '机床ID不能为空',
                    'data': None
                }
            
            if not machine_model:
                return {
                    'success': False,
                    'message': '机床型号不能为空',
                    'data': None
                }
            
            if comprehensive_score is None:
                return {
                    'success': False,
                    'message': '综合得分不能为空',
                    'data': None
                }
            
            if total_weight is None:
                return {
                    'success': False,
                    'message': '总权重不能为空',
                    'data': None
                }
            
            valid_machine_types = [choice[0] for choice in ComprehensiveWeightResultDameng.MACHINE_TYPE_CHOICES]
            if machine_type not in valid_machine_types:
                return {
                    'success': False,
                    'message': f'机床类型必须是以下值之一: {", ".join(valid_machine_types)}',
                    'data': None
                }
            
            with transaction.atomic():
                # 查询现有记录
                # 注意：达梦数据库不支持 select_for_update
                # 使用数据库事务保证数据一致性
                existing_record = ComprehensiveWeightResultDameng.objects.filter(
                    report_number=report_number
                ).first()
                
                if existing_record:
                    old_values = {
                        'machine_type': existing_record.machine_type,
                        'report_number': existing_record.report_number,
                        'machine_id': existing_record.machine_id,
                        'machine_model': existing_record.machine_model,
                        'comprehensive_score': float(existing_record.comprehensive_score),
                        'total_weight': float(existing_record.total_weight),
                        'precision_score': float(existing_record.precision_score),
                        'performance_score': float(existing_record.performance_score),
                        'reliability_score': float(existing_record.reliability_score),
                        'intelligence_score': float(existing_record.intelligence_score),
                        'green_score': float(existing_record.green_score)
                    }
                    
                    # 保留其他维度的得分（如果传入的值为0）
                    if performance_score == 0 and existing_record.performance_score:
                        performance_score = float(existing_record.performance_score)
                    if reliability_score == 0 and existing_record.reliability_score:
                        reliability_score = float(existing_record.reliability_score)
                    if intelligence_score == 0 and existing_record.intelligence_score:
                        intelligence_score = float(existing_record.intelligence_score)
                    if green_score == 0 and existing_record.green_score:
                        green_score = float(existing_record.green_score)
                    
                    existing_record.machine_type = machine_type
                    existing_record.machine_id = machine_id
                    existing_record.machine_model = machine_model
                    existing_record.total_weight = total_weight
                    existing_record.precision_score = precision_score
                    existing_record.performance_score = performance_score
                    existing_record.reliability_score = reliability_score
                    existing_record.intelligence_score = intelligence_score
                    existing_record.green_score = green_score
                    existing_record.evaluator = user
                    existing_record.version += 1
                    
                    existing_record.save()
                    
                    updated_comprehensive_score = float(existing_record.comprehensive_score)
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='UPDATE',
                        operation_details=f"更新综合权重计算结果: {report_number} - {machine_model}",
                        old_values=old_values,
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'comprehensive_score': updated_comprehensive_score,
                            'total_weight': float(total_weight),
                            'precision_score': float(precision_score),
                            'performance_score': float(performance_score),
                            'reliability_score': float(reliability_score),
                            'intelligence_score': float(intelligence_score),
                            'green_score': float(green_score)
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功更新综合权重计算结果: {report_number} - {machine_model} - {updated_comprehensive_score}分 (版本: {existing_record.version})")
                    
                    return {
                        'success': True,
                        'message': '更新成功',
                        'data': {
                            'id': existing_record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'comprehensive_score': updated_comprehensive_score,
                            'total_weight': float(total_weight),
                            'precision_score': float(precision_score),
                            'performance_score': float(performance_score),
                            'reliability_score': float(reliability_score),
                            'intelligence_score': float(intelligence_score),
                            'green_score': float(green_score),
                            'evaluator': user,
                            'calculated_at': existing_record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': existing_record.version,
                            'operation': 'update'
                        }
                    }
                else:
                    record = ComprehensiveWeightResultDameng.objects.create(
                        machine_type=machine_type,
                        report_number=report_number,
                        machine_id=machine_id,
                        machine_model=machine_model,
                        comprehensive_score=comprehensive_score,
                        total_weight=total_weight,
                        precision_score=precision_score,
                        performance_score=performance_score,
                        reliability_score=reliability_score,
                        intelligence_score=intelligence_score,
                        green_score=green_score,
                        evaluator=user
                    )
                    
                    created_comprehensive_score = float(record.comprehensive_score)
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='CREATE',
                        operation_details=f"保存综合权重计算结果: {report_number} - {machine_model}",
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'comprehensive_score': created_comprehensive_score,
                            'total_weight': float(total_weight),
                            'precision_score': float(precision_score),
                            'performance_score': float(performance_score),
                            'reliability_score': float(reliability_score),
                            'intelligence_score': float(intelligence_score),
                            'green_score': float(green_score)
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功保存综合权重计算结果: {report_number} - {machine_model} - {created_comprehensive_score}分")
                    
                    return {
                        'success': True,
                        'message': '保存成功',
                        'data': {
                            'id': record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'comprehensive_score': created_comprehensive_score,
                            'total_weight': float(total_weight),
                            'precision_score': float(precision_score),
                            'performance_score': float(performance_score),
                            'reliability_score': float(reliability_score),
                            'intelligence_score': float(intelligence_score),
                            'green_score': float(green_score),
                            'evaluator': user,
                            'calculated_at': record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': record.version,
                            'operation': 'create'
                        }
                    }
                
        except Exception as e:
            logger.error(f"保存综合权重计算结果失败: {str(e)}")
            return {
                'success': False,
                'message': f'保存失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_comprehensive_weight_result_by_report_number(report_number):
        """根据报告编号查询综合权重计算结果"""
        from ..models_dameng import ComprehensiveWeightResultDameng
        
        try:
            if not report_number:
                return {
                    'success': False,
                    'message': '报告编号不能为空',
                    'data': None
                }
            
            record = ComprehensiveWeightResultDameng.objects.filter(report_number=report_number).first()
            
            if not record:
                return {
                    'success': False,
                    'message': f'未找到报告编号为 {report_number} 的记录',
                    'data': None
                }
            
            return {
                'success': True,
                'message': '查询成功',
                'data': {
                    'id': record.id,
                    'machine_type': record.machine_type,
                    'report_number': record.report_number,
                    'machine_model': record.machine_model,
                    'comprehensive_score': float(record.comprehensive_score),
                    'total_weight': float(record.total_weight),
                    'precision_score': float(record.precision_score),
                    'performance_score': float(record.performance_score),
                    'reliability_score': float(record.reliability_score),
                    'intelligence_score': float(record.intelligence_score),
                    'green_score': float(record.green_score),
                    'evaluator': record.evaluator,
                    'calculated_at': record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'version': record.version
                }
            }
            
        except Exception as e:
            logger.error(f"查询综合权重计算结果失败: {str(e)}")
            return {
                'success': False,
                'message': f'查询失败: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def get_all_comprehensive_weight_results():
        """获取所有综合权重计算结果列表"""
        from ..models_dameng import ComprehensiveWeightResultDameng
        
        try:
            records = ComprehensiveWeightResultDameng.objects.all()
            
            results = []
            for record in records:
                results.append({
                    'id': record.id,
                    'machine_type': record.machine_type,
                    'report_number': record.report_number,
                    'machine_id': record.machine_id,
                    'machine_model': record.machine_model,
                    'comprehensive_score': float(record.comprehensive_score),
                    'total_weight': float(record.total_weight),
                    'precision_score': float(record.precision_score),
                    'performance_score': float(record.performance_score),
                    'reliability_score': float(record.reliability_score),
                    'intelligence_score': float(record.intelligence_score),
                    'green_score': float(record.green_score),
                    'evaluator': record.evaluator,
                    'calculated_at': record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'version': record.version
                })
            
            return {
                'success': True,
                'message': '查询成功',
                'data': results,
                'count': len(results)
            }
            
        except Exception as e:
            logger.error(f"查询所有综合权重计算结果失败: {str(e)}")
            return {
                'success': False,
                'message': f'查询失败: {str(e)}',
                'data': None,
                'count': 0
            }
    
    @staticmethod
    def save_reliability_score(machine_type, report_number, machine_id, machine_model, reliability_score, 
                             mtbf_score=0, mttr_score=0, availability_score=0, failure_rate_score=0, 
                             consistency_score=0, precision_retention_score=0, mttf_score=0,
                             user='unknown', ip_address='127.0.0.1'):
        """保存可靠性评分（MTBF、MTTR、可用性、故障率、一致性、精度保持性、MTTF）"""
        from ..models_dameng import ComprehensiveWeightResultDameng
        from datetime import datetime
        
        try:
            if not machine_type:
                return {
                    'success': False,
                    'message': '机床类型不能为空',
                    'data': None
                }
            
            if not report_number:
                return {
                    'success': False,
                    'message': '报告编号不能为空',
                    'data': None
                }
            
            if machine_id is None:
                return {
                    'success': False,
                    'message': '机床ID不能为空',
                    'data': None
                }
            
            if not machine_model:
                return {
                    'success': False,
                    'message': '机床型号不能为空',
                    'data': None
                }
            
            if reliability_score is None:
                return {
                    'success': False,
                    'message': '可靠性得分不能为空',
                    'data': None
                }
            
            if reliability_score < 60 or reliability_score > 100:
                return {
                    'success': False,
                    'message': '可靠性得分必须在60-100之间（百分制）',
                    'data': None
                }
            
            valid_machine_types = [choice[0] for choice in ComprehensiveWeightResultDameng.MACHINE_TYPE_CHOICES]
            if machine_type not in valid_machine_types:
                return {
                    'success': False,
                    'message': f'机床类型必须是以下值之一: {", ".join(valid_machine_types)}',
                    'data': None
                }
            
            with transaction.atomic():
                existing_record = ComprehensiveWeightResultDameng.objects.filter(
                    report_number=report_number
                ).first()
                
                if existing_record:
                    old_values = {
                        'machine_type': existing_record.machine_type,
                        'report_number': existing_record.report_number,
                        'machine_id': existing_record.machine_id,
                        'machine_model': existing_record.machine_model,
                        'reliability_score': float(existing_record.reliability_score) if existing_record.reliability_score else 0
                    }
                    
                    existing_record.machine_type = machine_type
                    existing_record.machine_id = machine_id
                    existing_record.machine_model = machine_model
                    existing_record.reliability_score = reliability_score
                    existing_record.evaluator = user
                    existing_record.version += 1
                    existing_record.save()
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='UPDATE',
                        operation_details=f"更新可靠性评分: {report_number} - {machine_model}",
                        old_values=old_values,
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'reliability_score': float(reliability_score),
                            'precision_score': float(existing_record.precision_score) if existing_record.precision_score else 0,
                            'performance_score': float(existing_record.performance_score) if existing_record.performance_score else 0,
                            'intelligence_score': float(existing_record.intelligence_score) if existing_record.intelligence_score else 0,
                            'green_score': float(existing_record.green_score) if existing_record.green_score else 0
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功更新可靠性评分: {report_number} - {machine_model} - {reliability_score}分 (版本: {existing_record.version})")
                    
                    return {
                        'success': True,
                        'message': '更新成功',
                        'data': {
                            'id': existing_record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'reliability_score': float(reliability_score),
                            'evaluator': user,
                            'calculated_at': existing_record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': existing_record.version,
                            'operation': 'update'
                        }
                    }
                else:
                    record = ComprehensiveWeightResultDameng.objects.create(
                        machine_type=machine_type,
                        report_number=report_number,
                        machine_id=machine_id,
                        machine_model=machine_model,
                        comprehensive_score=0,
                        total_weight=0,
                        reliability_score=reliability_score,
                        evaluator=user
                    )
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='CREATE',
                        operation_details=f"保存可靠性评分: {report_number} - {machine_model}",
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'reliability_score': float(reliability_score)
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功保存可靠性评分: {report_number} - {machine_model} - {reliability_score}分")
                    
                    return {
                        'success': True,
                        'message': '保存成功',
                        'data': {
                            'id': record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'reliability_score': float(reliability_score),
                            'evaluator': user,
                            'calculated_at': record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': record.version,
                            'operation': 'create'
                        }
                    }
        except Exception as e:
            logger.error(f"保存可靠性评分失败: {str(e)}")
            return {
                'success': False,
                'message': f'保存失败: {str(e)}',
                'data': None
            }

    @staticmethod
    def save_green_score(machine_type, report_number, machine_id, machine_model, green_score,
                         cutting_fluid_score=0, lubricant_score=0, lightweight_score=0,
                         energy_score=0, workpiece_score=0, volume_score=0,
                         standby_score=0, idle_score=0, cutting_score=0, cutting_energy_score=0,
                         user='unknown', ip_address='127.0.0.1'):
        """保存绿色化评分（切削液、润滑油、轻量化、能源、工件、体积等）"""
        from ..models_dameng import ComprehensiveWeightResultDameng
        from datetime import datetime
        
        try:
            if not machine_type:
                return {
                    'success': False,
                    'message': '机床类型不能为空',
                    'data': None
                }
            
            if not report_number:
                return {
                    'success': False,
                    'message': '报告编号不能为空',
                    'data': None
                }
            
            if machine_id is None:
                return {
                    'success': False,
                    'message': '机床ID不能为空',
                    'data': None
                }
            
            if not machine_model:
                return {
                    'success': False,
                    'message': '机床型号不能为空',
                    'data': None
                }
            
            if green_score is None:
                return {
                    'success': False,
                    'message': '绿色化得分不能为空',
                    'data': None
                }
            
            if green_score < 60 or green_score > 100:
                return {
                    'success': False,
                    'message': '绿色化得分必须在60-100之间（百分制）',
                    'data': None
                }
            
            valid_machine_types = [choice[0] for choice in ComprehensiveWeightResultDameng.MACHINE_TYPE_CHOICES]
            if machine_type not in valid_machine_types:
                return {
                    'success': False,
                    'message': f'机床类型必须是以下值之一: {", ".join(valid_machine_types)}',
                    'data': None
                }
            
            with transaction.atomic():
                existing_record = ComprehensiveWeightResultDameng.objects.filter(
                    report_number=report_number
                ).first()
                
                if existing_record:
                    old_values = {
                        'machine_type': existing_record.machine_type,
                        'report_number': existing_record.report_number,
                        'machine_id': existing_record.machine_id,
                        'machine_model': existing_record.machine_model,
                        'green_score': float(existing_record.green_score) if existing_record.green_score else 0
                    }
                    
                    existing_record.machine_type = machine_type
                    existing_record.machine_id = machine_id
                    existing_record.machine_model = machine_model
                    existing_record.green_score = green_score
                    existing_record.evaluator = user
                    existing_record.version += 1
                    existing_record.save()
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='UPDATE',
                        operation_details=f"更新绿色化评分: {report_number} - {machine_model}",
                        old_values=old_values,
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'green_score': float(green_score),
                            'precision_score': float(existing_record.precision_score) if existing_record.precision_score else 0,
                            'performance_score': float(existing_record.performance_score) if existing_record.performance_score else 0,
                            'reliability_score': float(existing_record.reliability_score) if existing_record.reliability_score else 0,
                            'intelligence_score': float(existing_record.intelligence_score) if existing_record.intelligence_score else 0
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功更新绿色化评分: {report_number} - {machine_model} - {green_score}分 (版本: {existing_record.version})")
                    
                    return {
                        'success': True,
                        'message': '更新成功',
                        'data': {
                            'id': existing_record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'green_score': float(green_score),
                            'evaluator': user,
                            'calculated_at': existing_record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': existing_record.version,
                            'operation': 'update'
                        }
                    }
                else:
                    record = ComprehensiveWeightResultDameng.objects.create(
                        machine_type=machine_type,
                        report_number=report_number,
                        machine_id=machine_id,
                        machine_model=machine_model,
                        comprehensive_score=0,
                        total_weight=0,
                        green_score=green_score,
                        evaluator=user
                    )
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='CREATE',
                        operation_details=f"保存绿色化评分: {report_number} - {machine_model}",
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'green_score': float(green_score)
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功保存绿色化评分: {report_number} - {machine_model} - {green_score}分")
                    
                    return {
                        'success': True,
                        'message': '保存成功',
                        'data': {
                            'id': record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'green_score': float(green_score),
                            'evaluator': user,
                            'calculated_at': record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': record.version,
                            'operation': 'create'
                        }
                    }
        except Exception as e:
            logger.error(f"保存绿色化评分失败: {str(e)}")
            return {
                'success': False,
                'message': f'保存失败: {str(e)}',
                'data': None
            }

    def save_performance_score(machine_type, report_number, machine_id, machine_model, performance_score,
                             dispersion_score=0, efficiency_score=0, static_stiffness_score=0,
                             spindle_score=0, noise_score=0, current_stability_score=0, thermal_deformation_score=0,
                             spindle_load_score=0, max_load_score=0, vibration_resistance_score=0,
                             user='unknown', ip_address='127.0.0.1'):
        """保存性能评分（离散性、效率、刚度、主轴、噪声、电流稳定性、热变形等）"""
        from ..models_dameng import ComprehensiveWeightResultDameng
        from datetime import datetime
        
        try:
            if not machine_type:
                return {
                    'success': False,
                    'message': '机床类型不能为空',
                    'data': None
                }
            
            if not report_number:
                return {
                    'success': False,
                    'message': '报告编号不能为空',
                    'data': None
                }
            
            if machine_id is None:
                return {
                    'success': False,
                    'message': '机床ID不能为空',
                    'data': None
                }
            
            if not machine_model:
                return {
                    'success': False,
                    'message': '机床型号不能为空',
                    'data': None
                }
            
            if performance_score is None:
                return {
                    'success': False,
                    'message': '性能得分不能为空',
                    'data': None
                }
            
            if performance_score < 60 or performance_score > 100:
                return {
                    'success': False,
                    'message': '性能得分必须在60-100之间（百分制）',
                    'data': None
                }
            
            valid_machine_types = [choice[0] for choice in ComprehensiveWeightResultDameng.MACHINE_TYPE_CHOICES]
            if machine_type not in valid_machine_types:
                return {
                    'success': False,
                    'message': f'机床类型必须是以下值之一: {", ".join(valid_machine_types)}',
                    'data': None
                }
            
            with transaction.atomic():
                existing_record = ComprehensiveWeightResultDameng.objects.filter(
                    report_number=report_number
                ).first()
                
                if existing_record:
                    old_values = {
                        'machine_type': existing_record.machine_type,
                        'report_number': existing_record.report_number,
                        'machine_id': existing_record.machine_id,
                        'machine_model': existing_record.machine_model,
                        'performance_score': float(existing_record.performance_score) if existing_record.performance_score else 0
                    }
                    
                    existing_record.machine_type = machine_type
                    existing_record.machine_id = machine_id
                    existing_record.machine_model = machine_model
                    existing_record.performance_score = performance_score
                    existing_record.evaluator = user
                    existing_record.version += 1
                    existing_record.save()
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='UPDATE',
                        operation_details=f"更新性能评分: {report_number} - {machine_model}",
                        old_values=old_values,
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'performance_score': float(performance_score),
                            'precision_score': float(existing_record.precision_score) if existing_record.precision_score else 0,
                            'reliability_score': float(existing_record.reliability_score) if existing_record.reliability_score else 0,
                            'intelligence_score': float(existing_record.intelligence_score) if existing_record.intelligence_score else 0,
                            'green_score': float(existing_record.green_score) if existing_record.green_score else 0
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功更新性能评分: {report_number} - {machine_model} - {performance_score}分 (版本: {existing_record.version})")
                    
                    return {
                        'success': True,
                        'message': '更新成功',
                        'data': {
                            'id': existing_record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'performance_score': float(performance_score),
                            'evaluator': user,
                            'calculated_at': existing_record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': existing_record.version,
                            'operation': 'update'
                        }
                    }
                else:
                    record = ComprehensiveWeightResultDameng.objects.create(
                        machine_type=machine_type,
                        report_number=report_number,
                        machine_id=machine_id,
                        machine_model=machine_model,
                        comprehensive_score=0,
                        total_weight=0,
                        performance_score=performance_score,
                        evaluator=user
                    )
                    
                    OperationLog.objects.create(
                        machine_id=0,
                        operation_type='CREATE',
                        operation_details=f"保存性能评分: {report_number} - {machine_model}",
                        new_values={
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'performance_score': float(performance_score)
                        },
                        operated_by=user,
                        ip_address=ip_address
                    )
                    
                    logger.info(f"成功保存性能评分: {report_number} - {machine_model} - {performance_score}分")
                    
                    return {
                        'success': True,
                        'message': '保存成功',
                        'data': {
                            'id': record.id,
                            'machine_type': machine_type,
                            'report_number': report_number,
                            'machine_id': machine_id,
                            'machine_model': machine_model,
                            'performance_score': float(performance_score),
                            'evaluator': user,
                            'calculated_at': record.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'version': record.version,
                            'operation': 'create'
                        }
                    }
        except Exception as e:
            logger.error(f"保存性能评分失败: {str(e)}")
            return {
                'success': False,
                'message': f'保存失败: {str(e)}',
                'data': None
            }