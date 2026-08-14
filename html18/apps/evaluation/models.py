from django.db import models
from django.contrib.auth.models import User


class Machine(models.Model):
    """机床模型"""
    MACHINE_TYPES = [
        ('machining_center', '加工中心'),
        ('boring_milling_machine', '镗铣床'),
    ]

    machine_type = models.CharField(max_length=30, choices=MACHINE_TYPES, verbose_name="机床类型", default='machining_center')
    name = models.CharField(max_length=200, verbose_name="机床名称")
    machine_number = models.CharField(max_length=100, verbose_name="机床编号", null=True, blank=True)
    report_number = models.CharField(max_length=100, verbose_name="报告编号", null=True, blank=True)
    specification_model = models.CharField(max_length=100, verbose_name="规格型号", null=True, blank=True)
    manufacturer = models.CharField(max_length=100, verbose_name="生产厂家", null=True, blank=True)
    production_date = models.DateField(verbose_name="生产日期", null=True, blank=True)
    model = models.CharField(max_length=100, verbose_name="型号", null=True, blank=True)

    # 精度维度
    positioning_accuracy = models.FloatField(verbose_name="定位精度(mm)", null=True, blank=True)
    repeat_positioning_accuracy = models.FloatField(verbose_name="重复定位精度(mm)", null=True, blank=True)

    # 加工中心特定参数
    x_axis_travel = models.FloatField(verbose_name="X轴行程(mm)", null=True, blank=True)
    y_axis_travel = models.FloatField(verbose_name="Y轴行程(mm)", null=True, blank=True)
    z_axis_travel = models.FloatField(verbose_name="Z轴行程(mm)", null=True, blank=True)
    worktable_length = models.FloatField(verbose_name="工作台短边长度Lb(mm)", null=True, blank=True)
    worktable_length_lc = models.FloatField(verbose_name="工作台长边长度Lc(mm)", null=True, blank=True)
    workpiece_size = models.IntegerField(verbose_name="工件尺寸(mm)", null=True, blank=True)
    spindle_type = models.CharField(max_length=20, verbose_name="主轴类型", null=True, blank=True)
    
    # 镗铣床特定参数（新增）
    column_measurement_range = models.FloatField(verbose_name="立柱测量范围(mm)", null=True, blank=True)
    worktable_x_range = models.FloatField(verbose_name="工作台X轴测量范围(mm)", null=True, blank=True)
    spindle_box_y_range = models.FloatField(verbose_name="主轴箱Y轴测量范围(mm)", null=True, blank=True)
    z_axis_measurement_range = models.FloatField(verbose_name="数控镗轴或滑枕(Z轴)测量范围(mm)", null=True, blank=True)
    boring_axis_diameter = models.FloatField(verbose_name="镗轴直径(mm)", null=True, blank=True)
    milling_axis_diameter = models.FloatField(verbose_name="铣轴直径(mm)", null=True, blank=True)
    worktable_type = models.CharField(max_length=50, verbose_name="工作台类型", null=True, blank=True)

    # 关联的允差值（组别1）
    tolerance_group_1 = models.JSONField(verbose_name="组别1允差值", null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    admin_saved = models.BooleanField(default=False, verbose_name="管理员已保存")

    def __str__(self):
        # 如果有报告编号，显示报告编号；否则显示型号
        if self.report_number:
            return f"{self.name} ({self.report_number})"
        return f"{self.name} ({self.model})"

    class Meta:
        verbose_name = "机床"
        verbose_name_plural = "机床管理"
        unique_together = [['report_number', 'created_by']]


class Evaluation(models.Model):
    """质量评价模型"""
    GRADE_CHOICES = [
        ('A+', '卓越 (≥90分)'),
        ('A', '优秀 (80-89分)'),
        ('B', '良好 (70-79分)'),
        ('C', '合格 (60-69分)'),
        ('D', '不合格 (<60分)'),
    ]

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="评价机床")
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="评价人")

    # 各维度得分
    accuracy_score = models.FloatField(verbose_name="精度得分", default=0)
    reliability_score = models.FloatField(verbose_name="可靠性得分", default=0)
    performance_score = models.FloatField(verbose_name="性能得分", default=0)
    intelligence_score = models.FloatField(verbose_name="智能化得分", default=0)
    green_score = models.FloatField(verbose_name="绿色化得分", default=0)

    # 总体评价
    total_score = models.FloatField(verbose_name="总得分", default=0)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, verbose_name="质量等级", default='C')

    evaluation_date = models.DateTimeField(auto_now_add=True, verbose_name="评价日期")
    notes = models.TextField(verbose_name="备注", blank=True)

    def __str__(self):
        return f"{self.machine.name} - {self.grade}"

    class Meta:
        verbose_name = "质量评价"
        verbose_name_plural = "质量评价记录"


class AHPMatrix(models.Model):
    """AHP判断矩阵模型"""
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="评价人")
    path = models.CharField(max_length=200, verbose_name="评价路径", blank=True)
    indicator_names = models.JSONField(verbose_name="指标名称列表")
    matrix_data = models.JSONField(verbose_name="判断矩阵数据")
    weights = models.JSONField(verbose_name="权重结果", null=True, blank=True)
    consistency = models.JSONField(verbose_name="一致性检验结果", null=True, blank=True)
    is_consistent = models.BooleanField(verbose_name="是否通过一致性检验", default=False)
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    notes = models.TextField(verbose_name="备注", blank=True)

    def __str__(self):
        return f"{self.path} - {self.evaluator.username} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "AHP判断矩阵"
        verbose_name_plural = "AHP判断矩阵记录"
        ordering = ['-submitted_at']


class EntropyWeight(models.Model):
    """信息熵权重计算模型"""
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="计算人")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="评价机床", null=True, blank=True)
    
    # 精度数据类型
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
    precision_type = models.CharField(max_length=20, choices=PRECISION_TYPE_CHOICES, verbose_name="精度数据类型", default='feed_axis')
    
    # 总ID相关字段
    total_id = models.CharField(max_length=100, verbose_name="总ID", unique=True, db_index=True, default="TEMP_ID")
    
    sample_count = models.IntegerField(verbose_name="样本数量")
    indicator_names = models.JSONField(verbose_name="指标名称列表")
    input_data = models.JSONField(verbose_name="输入数据")
    entropy_values = models.JSONField(verbose_name="信息熵值")
    weights = models.JSONField(verbose_name="权重结果")
    tolerance_values = models.JSONField(verbose_name="允差值", blank=True, null=True)
    standard_values = models.JSONField(verbose_name="标准值", blank=True, null=True)
    description = models.CharField(max_length=200, verbose_name="描述", blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="计算时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    notes = models.TextField(verbose_name="备注", blank=True)
    
    # 乐观锁字段
    version = models.IntegerField(default=0, verbose_name="版本号")

    def __str__(self):
        machine_name = self.machine.name if self.machine else "未指定"
        return f"{machine_name} - 信息熵权重 - {self.evaluator.username} - {self.calculated_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "信息熵权重计算"
        verbose_name_plural = "信息熵权重计算记录"
        ordering = ['-calculated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['machine', 'precision_type'],
                name='unique_machine_precision_entropy_weight',
                violation_error_message='同一机床ID和精度数据类型组合在系统中仅存在一条关联总ID记录'
            )
        ]


class ComprehensiveWeightResult(models.Model):
    """综合权重计算结果模型"""
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="计算人")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="评价机床")
    
    # 组合系数
    alpha = models.FloatField(verbose_name="组合系数α", default=0.5)
    
    # 权重数据
    ahp_weights = models.JSONField(verbose_name="AHP权重")
    entropy_weights = models.JSONField(verbose_name="信息熵权重")
    combined_weights = models.JSONField(verbose_name="局部组合权重")
    
    # 指标数据
    measured_values = models.JSONField(verbose_name="测量值")
    standard_values = models.JSONField(verbose_name="标准值")
    tolerances = models.JSONField(verbose_name="允差值")
    
    # 计算结果
    global_weights = models.JSONField(verbose_name="全局权重")
    indicator_scores = models.JSONField(verbose_name="指标得分")
    weighted_scores = models.JSONField(verbose_name="加权得分")
    
    # 总体评价
    total_score = models.FloatField(verbose_name="总得分", default=0)
    grade = models.CharField(max_length=2, choices=Evaluation.GRADE_CHOICES, verbose_name="质量等级", default='C')
    
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="计算时间")
    notes = models.TextField(verbose_name="备注", blank=True)

    def __str__(self):
        return f"{self.machine.name} - 综合权重计算 - {self.evaluator.username} - {self.calculated_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "综合权重计算结果"
        verbose_name_plural = "综合权重计算结果记录"
        ordering = ['-calculated_at']


class UserEvaluationResult(models.Model):
    """用户评价结果模型 - 存储用户评价界面中的指标得分最低值及相关数据"""
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="评价机床")
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="评价人")
    
    # 几何精度数据
    feed_axis_accuracy = models.JSONField(verbose_name="进给轴精度数据", blank=True, null=True)
    feed_axis_straightness_min_score = models.FloatField(verbose_name="直线度", default=0)
    feed_axis_parallelism_min_score = models.FloatField(verbose_name="平行度", default=0)
    feed_axis_angle_min_score = models.FloatField(verbose_name="角度误差", default=0)
    feed_axis_perpendicularity_min_score = models.FloatField(verbose_name="垂直度", default=0)
    worktable_accuracy = models.JSONField(verbose_name="工作台精度数据", blank=True, null=True)
    worktable_flatness_min_score = models.FloatField(verbose_name="平面度", default=0)
    worktable_tslot_min_score = models.FloatField(verbose_name="T型槽平行度", default=0)
    worktable_straightness_min_score = models.FloatField(verbose_name="直线度", default=0)
    worktable_parallelism_min_score = models.FloatField(verbose_name="平行度(镗铣床)", default=0)
    spindle_accuracy = models.JSONField(verbose_name="主轴精度数据", blank=True, null=True)
    spindle_radial_min_score = models.FloatField(verbose_name="主轴径向跳动", default=0)
    spindle_axial_min_score = models.FloatField(verbose_name="主轴轴向窜动", default=0)
    spindle_face_min_score = models.FloatField(verbose_name="主轴端面跳动", default=0)
    # 主轴精度新的五个指标
    roundness = models.JSONField(verbose_name="圆度数据", blank=True, null=True)
    roundness_min_score = models.FloatField(verbose_name="圆度", default=0)
    coaxiality = models.JSONField(verbose_name="同轴度数据", blank=True, null=True)
    coaxiality_min_score = models.FloatField(verbose_name="同轴度", default=0)
    spindle_radial_runout = models.JSONField(verbose_name="主轴径向跳动数据", blank=True, null=True)
    spindle_radial_runout_min_score = models.FloatField(verbose_name="主轴径向跳动", default=0)
    spindle_end_runout = models.JSONField(verbose_name="主轴端面跳动数据", blank=True, null=True)
    spindle_end_runout_min_score = models.FloatField(verbose_name="主轴端面跳动", default=0)
    spindle_axial_runout = models.JSONField(verbose_name="主轴轴向窜动数据", blank=True, null=True)
    spindle_axial_runout_min_score = models.FloatField(verbose_name="主轴轴向窜动", default=0)
    tool_magazine_accuracy = models.JSONField(verbose_name="刀库精度数据", blank=True, null=True)
    tool_magazine_positioning_min_score = models.FloatField(verbose_name="刀库定位精度", default=0)
    tool_magazine_repeatability_min_score = models.FloatField(verbose_name="刀库重复定位精度", default=0)
    
    # 位置精度数据
    position_accuracy = models.JSONField(verbose_name="位置精度数据", blank=True, null=True)
    position_repeatability_min_score = models.FloatField(verbose_name="重复定位精度", default=0)
    position_positioning_min_score = models.FloatField(verbose_name="定位精度", default=0)
    position_offset_min_score = models.FloatField(verbose_name="平均位置偏移", default=0)
    position_deviation_min_score = models.FloatField(verbose_name="定位系统偏差", default=0)
    position_resolution_min_score = models.FloatField(verbose_name="最小分辨率", default=0)
    position_backlash_min_score = models.FloatField(verbose_name="反向间隙（差值）", default=0)
    
    # 加工精度数据
    machining_accuracy = models.JSONField(verbose_name="加工精度数据", blank=True, null=True)
    machining_surface_roughness_min_score = models.FloatField(verbose_name="表面粗糙度", default=0)
    machining_process_capability_min_score = models.FloatField(verbose_name="加工工序能力", default=0)
    machining_dimension_min_score = models.FloatField(verbose_name="尺寸精度", default=0)
    machining_geometry_min_score = models.FloatField(verbose_name="形状精度", default=0)
    
    # 运动精度数据
    motion_accuracy = models.JSONField(verbose_name="运动精度数据", blank=True, null=True)
    motion_spindle_min_score = models.FloatField(verbose_name="主轴径向误差", default=0)
    motion_axial_min_score = models.FloatField(verbose_name="主轴轴向误差", default=0)
    motion_angle_min_score = models.FloatField(verbose_name="主轴角度误差", default=0)
    motion_start_stop_min_score = models.FloatField(verbose_name="主轴启停响应时间", default=0)
    motion_balance_min_score = models.FloatField(verbose_name="主轴高速旋转时的动平衡精度", default=0)
    motion_multi_axis_min_score = models.FloatField(verbose_name="多轴联动精度", default=0)
    motion_transmission_min_score = models.FloatField(verbose_name="传动精度", default=0)
    motion_thermal_min_score = models.FloatField(verbose_name="进给轴热误差", default=0)
    motion_wear_min_score = models.FloatField(verbose_name="磨损精度", default=0)
    motion_flatness_min_score = models.FloatField(verbose_name="平面圆度误差", default=0)
    motion_profile_min_score = models.FloatField(verbose_name="轮廓精度", default=0)
    motion_space_min_score = models.FloatField(verbose_name="空间精度", default=0)
    motion_rtcp_min_score = models.FloatField(verbose_name="动态RTCP精度", default=0)
    motion_line_min_score = models.FloatField(verbose_name="直线、圆弧插补轨迹误差", default=0)
    motion_servo_min_score = models.FloatField(verbose_name="伺服跟随误差", default=0)
    motion_overshoot_min_score = models.FloatField(verbose_name="高速移动时“过冲”或“滞后”", default=0)
    motion_crawl_min_score = models.FloatField(verbose_name="低速移动时“爬行”", default=0)
    motion_tool_wear_min_score = models.FloatField(verbose_name="刀具磨损", default=0)
    motion_grinding_wear_min_score = models.FloatField(verbose_name="砂轮磨损（磨床）", default=0)
    
    # 允差数据
    tolerance_data = models.JSONField(verbose_name="允差数据", blank=True, null=True)
    
    # 信息熵权重数据
    entropy_weights = models.JSONField(verbose_name="信息熵权重", blank=True, null=True)
    
    # 标准值数据
    standard_values = models.JSONField(verbose_name="标准值", blank=True, null=True)
    
    # 总体评价
    total_score = models.FloatField(verbose_name="总得分", default=0)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.machine.name} - 用户评价结果 - {self.evaluator.username} - {self.updated_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "用户评价结果"
        verbose_name_plural = "用户评价结果记录"
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['machine'],
                name='unique_machine_evaluation'
            )
        ]


class DataOperationLog(models.Model):
    """数据操作日志模型"""
    ACTION_CHOICES = [
        ('INSERT', '创建'),
        ('UPDATE', '更新'),
        ('DELETE', '删除'),
    ]
    
    operator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="操作人员")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="操作类型")
    table_name = models.CharField(max_length=100, verbose_name="表名")
    record_id = models.CharField(max_length=100, verbose_name="记录ID")
    machine_id = models.IntegerField(verbose_name="机床ID", db_index=True)
    old_data = models.JSONField(verbose_name="旧数据", blank=True, null=True)
    new_data = models.JSONField(verbose_name="新数据", blank=True, null=True)
    ip_address = models.CharField(max_length=50, verbose_name="操作IP", blank=True)
    user_agent = models.CharField(max_length=200, verbose_name="用户代理", blank=True)
    operation_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    notes = models.TextField(verbose_name="备注", blank=True)

    def __str__(self):
        return f"{self.get_action_display()} - {self.table_name} - {self.record_id} - {self.operator.username} - {self.operation_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "数据操作日志"
        verbose_name_plural = "数据操作日志记录"
        ordering = ['-operation_time']


class SystemSettings(models.Model):
    """系统设置模型 - 存储系统级配置参数"""
    key = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="配置键")
    value = models.CharField(max_length=500, verbose_name="配置值")
    description = models.CharField(max_length=500, blank=True, verbose_name="配置描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = "系统设置"
        ordering = ['key']
