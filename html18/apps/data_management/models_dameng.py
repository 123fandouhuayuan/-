"""
达梦数据库模型定义
"""
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class MachineParameters(models.Model):
    """机床参数模型 - 仅用于加工中心"""
    
    MACHINE_TYPE_CHOICES = [
        ('machining_center', '加工中心'),
        ('boring_milling_machine', '镗铣床'),
    ]
    
    SPINDLE_TYPE_CHOICES = [
        ('integral', '整体主轴'),
        ('attached', '附加主轴'),
    ]
    
    machine_id = models.BigIntegerField(unique=True, verbose_name='机床ID')
    machine_type = models.CharField(max_length=50, choices=MACHINE_TYPE_CHOICES, verbose_name='机床类型')
    
    x_axis_travel = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='X轴行程(mm)')
    y_axis_travel = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴行程(mm)')
    z_axis_travel = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Z轴行程(mm)')
    worktable_length = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台长度(mm)')
    workpiece_size = models.IntegerField(null=True, blank=True, verbose_name='工件尺寸(mm)')
    spindle_type = models.CharField(max_length=20, choices=SPINDLE_TYPE_CHOICES, null=True, blank=True, verbose_name='主轴类型')
    
    x_axis_linearity_xy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='X轴直线度（X-Y垂直平面内）')
    x_axis_linearity_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='X轴直线度（Z-X水平平面内）')
    z_axis_linearity_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Z轴直线度（Y-Z垂直平面内）')
    z_axis_linearity_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Z轴直线度（Z-X水平平面内）')
    y_axis_linearity_xy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴直线度（X-Y垂直平面内）')
    y_axis_linearity_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴直线度（Y-Z垂直平面内）')
    
    x_axis_angle_pitch = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='X轴角度偏差（俯仰）')
    x_axis_angle_yaw = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='X轴角度偏差（偏摆）')
    x_axis_angle_roll = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='X轴角度偏差（倾斜）')
    z_axis_angle_pitch = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Z轴角度偏差（俯仰）')
    z_axis_angle_yaw = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Z轴角度偏差（偏摆）')
    z_axis_angle_roll = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Z轴角度偏差（倾斜）')
    y_axis_angle_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴角度偏差（Y-Z垂直平面内）')
    y_axis_angle_xy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴角度偏差（X-Y垂直平面内）')
    y_axis_angle_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴角度偏差（ZX水平面内）')
    
    y_axis_perpendicularity_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴与X轴垂直度')
    y_axis_perpendicularity_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Y轴与Z轴垂直度')
    z_axis_perpendicularity_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Z轴与X轴垂直度')
    spindle_perpendicularity_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴轴线与X轴轴线运动间的垂直度')
    spindle_perpendicularity_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴轴线与Y轴轴线运动间的垂直度')
    
    worktable_flatness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台面平面度')
    worktable_parallelism_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='台面和X轴轴线运动间的平行度')
    worktable_parallelism_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='台面和Z轴轴线运动间的平行度')
    
    spindle_axial_runout = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴的周期性轴向窜动')
    spindle_radial_runout_near = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='靠近主轴端部的径向跳动')
    spindle_radial_runout_300mm = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='距主轴端部300mm处的径向跳动')
    spindle_parallelism_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴轴线与Z轴平行度（Y-Z平面）')
    spindle_parallelism_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴轴线与Z轴平行度（Z-X平面）')
    
    linear_axis_repeatability_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴双向重复定位精度')
    linear_axis_repeatability_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴双向重复定位精度')
    linear_axis_repeatability_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴双向重复定位精度')
    linear_axis_positioning_accuracy_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴双向定位精度')
    linear_axis_positioning_accuracy_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴双向定位精度')
    linear_axis_positioning_accuracy_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴双向定位精度')
    linear_axis_mean_deviation_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴平均双向位置偏差范围')
    linear_axis_mean_deviation_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴平均双向位置偏差范围')
    linear_axis_mean_deviation_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴平均双向位置偏差范围')
    linear_axis_system_deviation_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴双向定位系统偏差E')
    linear_axis_system_deviation_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴双向定位系统偏差E')
    linear_axis_system_deviation_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴双向定位系统偏差E')
    linear_axis_backlash_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴反向差值')
    linear_axis_backlash_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴反向差值')
    linear_axis_backlash_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴反向差值')
    
    rotary_axis_repeatability_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴双向重复定位精度')
    rotary_axis_repeatability_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴双向重复定位精度')
    rotary_axis_repeatability_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴双向重复定位精度')
    rotary_axis_positioning_accuracy_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴双向定位精度')
    rotary_axis_positioning_accuracy_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴双向定位精度')
    rotary_axis_positioning_accuracy_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴双向定位精度')
    rotary_axis_mean_deviation_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴平均双向位置偏差范围')
    rotary_axis_mean_deviation_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴平均双向位置偏差范围')
    rotary_axis_mean_deviation_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴平均双向位置偏差范围')
    rotary_axis_system_deviation_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴双向定位系统偏差E')
    rotary_axis_system_deviation_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴双向定位系统偏差E')
    rotary_axis_system_deviation_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴双向定位系统偏差E')
    rotary_axis_backlash_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴反向差值')
    rotary_axis_backlash_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴反向差值')
    rotary_axis_backlash_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴反向差值')
    
    cylindricity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='圆柱度')
    hole_perpendicularity_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='孔中心轴线与基准孔A的垂直度')
    side_linearity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='侧面的直线度')
    adjacent_perpendicularity_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='相邻面与基面B的垂直度')
    opposite_parallelism_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='相对面与基面B的平行度')
    side_linearity_2 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='侧面的直线度')
    side_inclination_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='侧面对基准B的倾斜度')
    circularity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='圆度')
    concentricity_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='外圆和内圆孔C的同心度')
    slope_linearity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='斜面的直线度')
    slope_inclination_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='3°角斜面对基准B的倾斜度')
    hole_position_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='孔相对于内孔C的位置度')
    concentricity_d = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='内孔与外孔D的同心度')
    
    # 加工性能参数
    cp_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='CP值')
    peak_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='峰值转速')
    valley_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='谷值转速')
    design_max_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计最大转速')
    max_fast_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最高快移速度')
    design_max_fast_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计最高速度')
    repeat_positioning_accuracy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最高速度下重复定位精度')
    max_feed_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大进给速度')
    target_max_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='目标最高速度')
    repeat_positioning_accuracy_feed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='R2及加速度下重复定位精度')
    
    # 刚度参数
    radial_stiffness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='径向刚度')
    axial_stiffness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='轴向刚度')
    radial_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='径向刚度机床类型')
    axial_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='轴向刚度机床类型')
    cutting_stiffness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削刚度')
    static_stiffness_accept = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='合格线')
    static_stiffness_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='静刚度 K_s')
    
    # 运行性能参数
    max_vibration_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大振动速度')
    noise_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='噪声值')
    noise_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='噪声机床类型')
    noise_weight = models.CharField(max_length=50, null=True, blank=True, verbose_name='重量选择')
    initial_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='初检功率')
    final_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='终检功率')
    current_unbalance = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电流不平衡量')
    current_fluctuation = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电流波动度')
    voltage_fluctuation_min = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电压波动下限')
    voltage_fluctuation_max = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电压波动上限')
    frequency_fluctuation_min = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='频率波动下限')
    frequency_fluctuation_max = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='频率波动上限')
    radial_thermal_displacement = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='径向热位移')
    radial_thermal_gradient = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='热平衡梯度 G1')
    axial_thermal_displacement = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='轴向热位移')
    axial_thermal_gradient = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='热平衡梯度 G2')
    
    # 负荷能力参数
    measured_max_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='实测主轴最大功率')
    design_max_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计主轴最大功率')
    cutting_vibration_speed1 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度1')
    measured_max_torque = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='实测主轴最大扭矩')
    design_max_torque = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计主轴最大扭矩')
    cutting_vibration_speed2 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度2')
    actual_load_weight = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='试验实际负重')
    max_design_weight = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大设计重量')
    actual_load_velocity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='试验运行速度')
    max_design_velocity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大设计速度')
    cutting_vibration_speed3 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度3')
    cutting_vibration_speed4 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度4')
    load_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='负荷能力机床类型')
    evaluation_scheme = models.CharField(max_length=50, null=True, blank=True, verbose_name='评价方案')
    max_cutting_width = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大切削宽度')
    tool_diameter = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='刀具直径')
    max_cutting_length = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大切削长度')
    expected_cutting_length = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='预期切削长度')
    max_length_diameter_ratio = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大径长比')
    design_length_diameter_ratio = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计径长比')
    
    # 可靠性模块参数 - MTBF
    total_run_time = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='MTBF总运行时间')
    fault_count = models.IntegerField(null=True, blank=True, verbose_name='MTBF故障次数')
    
    # 可靠性模块参数 - MTTR
    repair_time_values = models.JSONField(null=True, blank=True, verbose_name='MTTR修复时间列表')
    
    # 可靠性模块参数 - 故障率
    fatal_failure = models.IntegerField(null=True, blank=True, verbose_name='致命故障数')
    serious_failure = models.IntegerField(null=True, blank=True, verbose_name='严重故障数')
    general_failure = models.IntegerField(null=True, blank=True, verbose_name='一般故障数')
    operation_time = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='运行时间')
    
    # 可靠性模块参数 - 加工一致性
    standard_deviation = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='标准差')
    mean_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='均值')
    
    # 可靠性模块参数 - 加工精度保持性
    original_precision = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='原始精度')
    failure_precision = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='失效精度')
    initial_precision = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='初始精度')
    
    # 可靠性模块参数 - MTTF
    failure_time_values = models.JSONField(null=True, blank=True, verbose_name='MTTF故障时间列表')
    
    # 智能化模块参数
    intelligence_checkbox_states = models.JSONField(null=True, blank=True, verbose_name='智能化checkbox状态')
    
    # 绿色化模块参数 - 资源循环与耗材
    cutting_fluid_q = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削液消耗量Q')
    cutting_fluid_p = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削液主轴功率P1')
    lubricant_l = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='润滑油消耗量L')
    lubricant_p = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='润滑油主轴功率P2')
    lubricant_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='润滑油消耗限定值x')
    lightweight_items = models.JSONField(null=True, blank=True, verbose_name='轻量化设计项目')
    
    # 绿色化模块参数 - 能源
    est_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='待机功率Est')
    eu_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='空运转功率Eu')
    ec_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削功率Ec')
    n_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='材料去除率n')
    v_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削体积v')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'machine_parameters'
        verbose_name = '机床参数'
        verbose_name_plural = '机床参数'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"机床{self.machine_id}"
    
    def get_machine_type_display(self):
        return dict(self.MACHINE_TYPE_CHOICES).get(self.machine_type, self.machine_type)


class BoringMillingParameters(models.Model):
    """镗铣床参数模型 - 按照前端界面字段顺序重新配置"""
    
    WORKTABLE_TYPE_CHOICES = [
        ('fixed', '固定式'),
        ('rotary', '回转式'),
        ('indexing', '分度式'),
    ]
    
    machine_id = models.BigIntegerField(unique=True, verbose_name='机床ID')
    
    column_measurement_range = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='立柱测量范围(mm)')
    worktable_x_range = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台X轴测量范围(mm)')
    spindle_box_y_range = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴箱Y轴测量范围(mm)')
    z_axis_measurement_range = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='数控镗轴或滑枕(Z轴)测量范围(mm)')
    worktable_length_lc = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台长边长度(mm)')
    boring_axis_diameter = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗轴直径(mm)')
    milling_axis_diameter = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='铣轴直径(mm)')
    worktable_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='工作台类型')
    
    bm_column_linearity_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='立柱移动的直线度-YZ平面(EYW)')
    bm_column_linearity_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='立柱移动的直线度-ZX平面(EXW)')
    bm_worktable_x_linearity_xy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台移动(X轴)的直线度-XY平面(EYX)')
    bm_worktable_x_linearity_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台移动(X轴)的直线度-ZX平面(EZX)')
    bm_spindle_box_y_linearity_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴箱移动(Y轴)的直线度-YZ平面(EZY)')
    bm_spindle_box_y_linearity_xy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴箱移动(Y轴)的直线度-XY平面(EXY)')
    
    bm_column_angle_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='立柱移动的角度偏差-YZ平面(EAW)')
    bm_column_angle_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='立柱移动的角度偏差-ZX平面(EBW)')
    bm_column_angle_xy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='立柱移动的角度偏差-XY平面(ECW)')
    bm_worktable_x_angle_xy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台移动(X轴)的角度偏差-XY平面(ECX)')
    bm_worktable_x_angle_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台移动(X轴)的角度偏差-ZX平面(EBX)')
    bm_worktable_x_angle_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台移动(X轴)的角度偏差-YZ平面(EAX)')
    bm_spindle_box_y_angle_yz = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴箱移动(Y轴)的角度偏差-YZ平面(EAY)')
    bm_spindle_box_y_angle_zx = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴箱移动(Y轴)的角度偏差-ZX平面(EBY)')
    
    bm_worktable_x_column_perpendicularity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台移动(X轴)和立柱移动间的垂直度(/1000)')
    bm_spindle_box_y_worktable_x_perpendicularity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴箱移动(Y轴)对工作台移动(X轴)的垂直度(/1000)')
    bm_spindle_box_y_column_perpendicularity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='主轴箱移动(Y轴)对立柱移动的垂直度(/1000)')
    
    bm_worktable_flatness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台面平面度')
    bm_column_parallelism = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='立柱移动的平行度')
    bm_worktable_x_parallelism = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='工作台移动(X轴)的平行度')
    
    bm_boring_axis_taper_radial_near = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗轴锥孔的径向跳动-靠近轴端部处')
    bm_boring_axis_taper_radial_300mm = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗轴锥孔的径向跳动-距镗轴端部300mm处')
    bm_boring_axis_radial_retracted = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗轴的径向跳动-镗轴缩回时')
    bm_boring_axis_radial_extended = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗轴的径向跳动-镗轴伸出300mm时')
    bm_milling_axis_radial = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='铣轴端部的径向跳动')
    bm_boring_axis_axial_retracted = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗轴周期性的轴向窜动-主轴缩回')
    bm_milling_axis_axial = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='铣轴端部的周期性轴向窜动')
    
    bm_linear_axis_repeatability_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴双向重复定位精度')
    bm_linear_axis_repeatability_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴双向重复定位精度')
    bm_linear_axis_repeatability_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴双向重复定位精度')
    bm_linear_axis_repeatability_w = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴W轴双向重复定位精度')
    bm_linear_axis_positioning_accuracy_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴双向定位精度')
    bm_linear_axis_positioning_accuracy_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴双向定位精度')
    bm_linear_axis_positioning_accuracy_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴双向定位精度')
    bm_linear_axis_positioning_accuracy_w = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴W轴双向定位精度')
    bm_linear_axis_mean_deviation_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴平均双向位置偏差范围')
    bm_linear_axis_mean_deviation_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴平均双向位置偏差范围')
    bm_linear_axis_mean_deviation_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴平均双向位置偏差范围')
    bm_linear_axis_mean_deviation_w = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴W轴平均双向位置偏差范围')
    bm_linear_axis_system_deviation_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴双向定位系统偏差E')
    bm_linear_axis_system_deviation_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴双向定位系统偏差E')
    bm_linear_axis_system_deviation_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴双向定位系统偏差E')
    bm_linear_axis_system_deviation_w = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴W轴双向定位系统偏差E')
    bm_linear_axis_backlash_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴X轴反向差值')
    bm_linear_axis_backlash_y = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Y轴反向差值')
    bm_linear_axis_backlash_z = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴Z轴反向差值')
    bm_linear_axis_backlash_w = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='线性轴W轴反向差值')
    
    bm_rotary_axis_repeatability_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴双向重复定位精度')
    bm_rotary_axis_repeatability_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴双向重复定位精度')
    bm_rotary_axis_repeatability_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴双向重复定位精度')
    bm_rotary_axis_positioning_accuracy_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴双向定位精度')
    bm_rotary_axis_positioning_accuracy_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴双向定位精度')
    bm_rotary_axis_positioning_accuracy_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴双向定位精度')
    bm_rotary_axis_mean_deviation_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴平均双向位置偏差范围')
    bm_rotary_axis_mean_deviation_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴平均双向位置偏差范围')
    bm_rotary_axis_mean_deviation_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴平均双向位置偏差范围')
    bm_rotary_axis_system_deviation_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴双向定位系统偏差E')
    bm_rotary_axis_system_deviation_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴双向定位系统偏差E')
    bm_rotary_axis_system_deviation_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴双向定位系统偏差E')
    bm_rotary_axis_backlash_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴A轴反向差值')
    bm_rotary_axis_backlash_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴B轴反向差值')
    bm_rotary_axis_backlash_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='回转轴C轴反向差值')
    
    bm_square_a = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='正方形-a')
    bm_square_b = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='正方形-b')
    bm_square_c = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='正方形-c')
    bm_square_d = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='正方形-d')
    bm_square_e = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='正方形-e')
    bm_square_f = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='正方形-f')
    bm_diamond_d = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='菱形-d')
    bm_diamond_e = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='菱形-e')
    bm_circle_f = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='圆-f')
    bm_circle_g = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='圆-g')
    bm_boring_hole_h = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗孔-h')
    bm_boring_hole_i = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='镗孔-i')
    
    bm_tool_magazine_positioning_accuracy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='刀库定位精度')
    bm_tool_magazine_repeatability = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='刀库重复定位精度')
    
    # 性能模块参数 - 加工性能
    cp_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='CP值')
    peak_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='峰值转速')
    valley_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='谷值转速')
    design_max_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计最大转速')
    max_fast_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最高快移速度')
    design_max_fast_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计最高速度')
    repeat_positioning_accuracy = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最高速度下重复定位精度')
    max_feed_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大进给速度')
    target_max_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='目标最高速度')
    repeat_positioning_accuracy_feed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='R2及加速度下重复定位精度')
    
    # 性能模块参数 - 刚度
    radial_stiffness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='径向刚度')
    axial_stiffness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='轴向刚度')
    radial_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='径向刚度机床类型')
    axial_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='轴向刚度机床类型')
    cutting_stiffness = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削刚度')
    static_stiffness_accept = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='合格线')
    static_stiffness_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='静刚度 K_s')
    
    # 性能模块参数 - 运行性能
    max_vibration_speed = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大振动速度')
    noise_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='噪声值')
    noise_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='噪声机床类型')
    noise_weight = models.CharField(max_length=50, null=True, blank=True, verbose_name='重量选择')
    initial_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='初检功率')
    final_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='终检功率')
    current_unbalance = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电流不平衡量')
    current_fluctuation = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电流波动度')
    voltage_fluctuation_min = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电压波动下限')
    voltage_fluctuation_max = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='电压波动上限')
    frequency_fluctuation_min = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='频率波动下限')
    frequency_fluctuation_max = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='频率波动上限')
    radial_thermal_displacement = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='径向热位移')
    radial_thermal_gradient = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='热平衡梯度 G1')
    axial_thermal_displacement = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='轴向热位移')
    axial_thermal_gradient = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='热平衡梯度 G2')
    
    # 性能模块参数 - 负荷能力
    measured_max_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='实测主轴最大功率')
    design_max_power = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计主轴最大功率')
    cutting_vibration_speed1 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度1')
    measured_max_torque = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='实测主轴最大扭矩')
    design_max_torque = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计主轴最大扭矩')
    cutting_vibration_speed2 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度2')
    actual_load_weight = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='试验实际负重')
    max_design_weight = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大设计重量')
    actual_load_velocity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='试验运行速度')
    max_design_velocity = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大设计速度')
    cutting_vibration_speed3 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度3')
    cutting_vibration_speed4 = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削振动速度4')
    load_machine_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='负荷能力机床类型')
    evaluation_scheme = models.CharField(max_length=50, null=True, blank=True, verbose_name='评价方案')
    max_cutting_width = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大切削宽度')
    tool_diameter = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='刀具直径')
    max_cutting_length = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大切削长度')
    expected_cutting_length = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='预期切削长度')
    max_length_diameter_ratio = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='最大径长比')
    design_length_diameter_ratio = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='设计径长比')
    
    # 可靠性模块参数 - MTBF
    total_run_time = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='MTBF总运行时间')
    fault_count = models.IntegerField(null=True, blank=True, verbose_name='MTBF故障次数')
    
    # 可靠性模块参数 - MTTR
    repair_time_values = models.JSONField(null=True, blank=True, verbose_name='MTTR修复时间列表')
    
    # 可靠性模块参数 - 故障率
    fatal_failure = models.IntegerField(null=True, blank=True, verbose_name='致命故障数')
    serious_failure = models.IntegerField(null=True, blank=True, verbose_name='严重故障数')
    general_failure = models.IntegerField(null=True, blank=True, verbose_name='一般故障数')
    operation_time = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='运行时间')
    
    # 可靠性模块参数 - 加工一致性
    standard_deviation = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='标准差')
    mean_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='均值')
    
    # 可靠性模块参数 - 加工精度保持性
    original_precision = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='原始精度')
    failure_precision = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='失效精度')
    initial_precision = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='初始精度')
    
    # 可靠性模块参数 - MTTF
    failure_time_values = models.JSONField(null=True, blank=True, verbose_name='MTTF故障时间列表')
    
    # 智能化模块参数
    intelligence_checkbox_states = models.JSONField(null=True, blank=True, verbose_name='智能化checkbox状态')
    
    # 绿色化模块参数 - 资源循环与耗材
    cutting_fluid_q = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削液消耗量Q')
    cutting_fluid_p = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削液主轴功率P1')
    lubricant_l = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='润滑油消耗量L')
    lubricant_p = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='润滑油主轴功率P2')
    lubricant_x = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='润滑油消耗限定值x')
    lightweight_items = models.JSONField(null=True, blank=True, verbose_name='轻量化设计项目')
    
    # 绿色化模块参数 - 能源
    est_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='待机功率Est')
    eu_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='空运转功率Eu')
    ec_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削功率Ec')
    n_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='材料去除率n')
    v_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='切削体积v')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='创建人')
    updated_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='更新人')
    
    class Meta:
        db_table = 'boring_milling_parameters'
        verbose_name = '镗铣床参数'
        verbose_name_plural = '镗铣床参数'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"镗铣床{self.machine_id}"


class OperationLog(models.Model):
    """操作日志模型"""
    
    OPERATION_TYPES = [
        ('CREATE', '创建'),
        ('UPDATE', '更新'),
        ('DELETE', '删除'),
        ('READ', '查询'),
    ]
    
    machine_id = models.BigIntegerField(verbose_name='机床ID')
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES, verbose_name='操作类型')
    operation_details = models.TextField(null=True, blank=True, verbose_name='操作详情')
    old_values = models.JSONField(null=True, blank=True, verbose_name='修改前值')
    new_values = models.JSONField(null=True, blank=True, verbose_name='修改后值')
    operated_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='操作人')
    operated_at = models.DateTimeField(default=timezone.now, verbose_name='操作时间')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    
    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-operated_at']
    
    def __str__(self):
        return f"{self.get_operation_type_display()} - 机床{self.machine_id}"


class EntropyWeightDameng(models.Model):
    """信息熵权重计算结果模型 - 达梦数据库"""
    
    MACHINE_TYPE_CHOICES = [
        ('machining_center', '加工中心'),
        ('boring_milling_machine', '镗铣床'),
    ]
    
    PRECISION_TYPE_CHOICES = [
        ('feed_axis', '进给轴精度'),
        ('worktable', '工作台精度'),
        ('spindle', '主轴精度'),
        ('position', '位置精度'),
        ('workpiece_geometry', '工件几何精度'),
        ('tool_magazine', '刀库精度'),
        ('spindle_motion', '主轴运动精度'),
        ('multi_axis', '多轴联动精度'),
        ('transmission', '传动精度'),
        ('thermal_error', '热误差'),
        ('wear', '磨损精度'),
    ]
    
    machine_type = models.CharField(max_length=50, choices=MACHINE_TYPE_CHOICES, verbose_name='机床类型', db_index=True)
    precision_type = models.CharField(max_length=30, choices=PRECISION_TYPE_CHOICES, verbose_name='精度数据类型', default='feed_axis')
    total_id = models.CharField(max_length=100, verbose_name='总ID', unique=True, db_index=True, default='TEMP_ID')
    
    sample_count = models.IntegerField(verbose_name='样本数量', default=0)
    indicator_names = models.JSONField(verbose_name='指标名称列表', null=True, blank=True)
    input_data = models.JSONField(verbose_name='输入数据', null=True, blank=True)
    entropy_values = models.JSONField(verbose_name='信息熵值', null=True, blank=True)
    weights = models.JSONField(verbose_name='权重结果', null=True, blank=True)
    tolerance_values = models.JSONField(verbose_name='允差值', null=True, blank=True)
    standard_values = models.JSONField(verbose_name='标准值', null=True, blank=True)
    description = models.CharField(max_length=500, verbose_name='描述', blank=True, default='')
    
    evaluator = models.CharField(max_length=50, verbose_name='计算人', null=True, blank=True)
    calculated_at = models.DateTimeField(default=timezone.now, verbose_name='计算时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    version = models.IntegerField(default=0, verbose_name='版本号')
    
    class Meta:
        db_table = 'entropy_weight_dameng'
        verbose_name = '信息熵权重计算结果'
        verbose_name_plural = '信息熵权重计算结果'
        ordering = ['-calculated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['machine_type', 'precision_type'],
                name='unique_machine_type_precision_entropy_dameng',
                violation_error_message='同一机床类型和精度数据类型组合在系统中仅存在一条关联总ID记录'
            )
        ]
    
    def __str__(self):
        return f"{self.get_machine_type_display()} - {self.get_precision_type_display()} - {self.calculated_at.strftime('%Y-%m-%d %H:%M')}"


class ComprehensiveWeightResultDameng(models.Model):
    """综合权重计算结果模型 - 达梦数据库"""
    
    MACHINE_TYPE_CHOICES = [
        ('machining_center', '加工中心'),
        ('boring_milling_machine', '镗铣床'),
    ]
    
    machine_type = models.CharField(max_length=50, choices=MACHINE_TYPE_CHOICES, verbose_name='机床类型', db_index=True)
    report_number = models.CharField(max_length=100, unique=True, verbose_name='报告编号', db_index=True)
    machine_id = models.IntegerField(verbose_name='机床 ID', db_index=True)
    machine_model = models.CharField(max_length=100, verbose_name='机床型号')
    comprehensive_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='综合得分')
    total_weight = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='总权重')
    
    precision_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='精度维度得分（百分制）')
    performance_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='性能维度得分（百分制）')
    reliability_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='可靠性维度得分（百分制）')
    intelligence_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='智能化维度得分（百分制）')
    green_score = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='绿色化维度得分（百分制）')
    
    evaluator = models.CharField(max_length=50, verbose_name='计算人', null=True, blank=True)
    calculated_at = models.DateTimeField(default=timezone.now, verbose_name='计算时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    version = models.IntegerField(default=0, verbose_name='版本号')
    
    class Meta:
        db_table = 'comprehensive_weight_result_dameng'
        verbose_name = '综合权重计算结果'
        verbose_name_plural = '综合权重计算结果'
        ordering = ['machine_id']
        constraints = [
            models.UniqueConstraint(
                fields=['report_number'],
                name='unique_report_number'
            )
        ]
    
    def __str__(self):
        return f"{self.report_number} - {self.machine_model} - {self.comprehensive_score}分"

    def get_ahp_weights(self):
        """从EVALUATION_AHPMATRIX表获取综合得分的权重配置"""
        try:
            from apps.evaluation.models import AHPMatrix
            ahp_matrix = AHPMatrix.objects.filter(path='综合得分').first()
            if ahp_matrix and ahp_matrix.weights and len(ahp_matrix.weights) == 5:
                return ahp_matrix.weights
        except Exception:
            pass
        return None

    def calculate_comprehensive_score(self):
        """动态计算综合得分

        计算公式：
        综合得分 = (精度分数 × 精度权重) +
                  (性能分数 × 性能权重) +
                  (可靠性分数 × 可靠性权重) +
                  (智能化分数 × 智能化权重) +
                  (绿色化分数 × 绿色化权重)

        注意：所有分数均为百分制，不再进行五分制转换
        """
        weights = self.get_ahp_weights()
        if not weights:
            return None

        try:
            precision = float(self.precision_score) if self.precision_score else 0
            performance = float(self.performance_score) if self.performance_score else 0
            reliability = float(self.reliability_score) if self.reliability_score else 0
            intelligence = float(self.intelligence_score) if self.intelligence_score else 0
            green = float(self.green_score) if self.green_score else 0

            # [FIX] 所有分数均为百分制，直接加权计算，不再进行五分制转百分制转换
            comprehensive_score = (
                precision * weights[0] +
                performance * weights[1] +
                reliability * weights[2] +
                intelligence * weights[3] +
                green * weights[4]
            )

            return round(comprehensive_score, 2)
        except Exception:
            return None

    @property
    def dynamic_comprehensive_score(self):
        """动态计算的综合得分属性

        该属性实时计算综合得分，不依赖数据库存储的值。
        当任意维度得分改变时，该属性会自动返回最新的计算结果。
        """
        return self.calculate_comprehensive_score()

    def save(self, *args, **kwargs):
        """重写save方法，实现数据联动机制

        当精度、性能、可靠性、智能化、绿色化五个指标中的任何一个分数值发生修改时，
        自动重新计算综合得分并更新。
        """
        force_update = kwargs.pop('force_update', False)

        if self.pk:
            try:
                old_instance = ComprehensiveWeightResultDameng.objects.get(pk=self.pk)

                score_fields = [
                    'precision_score',
                    'performance_score',
                    'reliability_score',
                    'intelligence_score',
                    'green_score'
                ]

                score_changed = any(
                    getattr(old_instance, field) != getattr(self, field)
                    for field in score_fields
                )

                if score_changed:
                    new_score = self.calculate_comprehensive_score()
                    if new_score is not None:
                        self.comprehensive_score = new_score
                        self.version += 1
            except ComprehensiveWeightResultDameng.DoesNotExist:
                pass
        else:
            new_score = self.calculate_comprehensive_score()
            if new_score is not None:
                self.comprehensive_score = new_score

        super().save(*args, **kwargs)
