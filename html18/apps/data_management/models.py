from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import uuid


class DataImportLog(models.Model):
    """数据导入日志模型"""
    IMPORT_STATUS = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('partial', '部分成功'),
    ]

    IMPORT_TYPE = [
        ('machine', '机床数据'),
        ('evaluation', '评价数据'),
        ('benchmark', '标杆数据'),
        ('other', '其他数据'),
    ]

    # 基本信息
    import_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="导入ID")
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE, verbose_name="导入类型")
    file_name = models.CharField(max_length=255, verbose_name="文件名")
    file_path = models.FileField(upload_to='imports/%Y/%m/%d/', verbose_name="文件路径", null=True, blank=True)

    # 处理信息
    total_records = models.IntegerField(verbose_name="总记录数", default=0)
    success_records = models.IntegerField(verbose_name="成功记录数", default=0)
    failed_records = models.IntegerField(verbose_name="失败记录数", default=0)
    status = models.CharField(max_length=20, choices=IMPORT_STATUS, default='pending', verbose_name="状态")

    # 错误信息
    error_message = models.TextField(verbose_name="错误信息", blank=True)
    error_details = models.JSONField(verbose_name="错误详情", null=True, blank=True)

    # 系统信息
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="导入人")
    start_time = models.DateTimeField(verbose_name="开始时间", auto_now_add=True)
    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    processing_time = models.DurationField(verbose_name="处理时长", null=True, blank=True)

    class Meta:
        verbose_name = "数据导入日志"
        verbose_name_plural = "数据导入日志"
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.get_import_type_display()} - {self.file_name} ({self.status})"


class DataExportLog(models.Model):
    """数据导出日志模型"""
    EXPORT_STATUS = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    EXPORT_FORMAT = [
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('pdf', 'PDF'),
    ]

    # 基本信息
    export_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="导出ID")
    export_name = models.CharField(max_length=255, verbose_name="导出名称")
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMAT, default='excel', verbose_name="导出格式")

    # 导出参数
    export_parameters = models.JSONField(verbose_name="导出参数", default=dict)
    data_filters = models.JSONField(verbose_name="数据筛选条件", default=dict)

    # 文件信息
    file_path = models.FileField(upload_to='exports/%Y/%m/%d/', verbose_name="文件路径", null=True, blank=True)
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)", default=0)

    # 处理信息
    status = models.CharField(max_length=20, choices=EXPORT_STATUS, default='pending', verbose_name="状态")
    error_message = models.TextField(verbose_name="错误信息", blank=True)

    # 系统信息
    exported_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="导出人")
    start_time = models.DateTimeField(verbose_name="开始时间", auto_now_add=True)
    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)

    class Meta:
        verbose_name = "数据导出日志"
        verbose_name_plural = "数据导出日志"
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.export_name} ({self.get_export_format_display()})"


class DataCleaningRule(models.Model):
    """数据清洗规则模型"""
    RULE_TYPE = [
        ('validation', '验证规则'),
        ('cleaning', '清洗规则'),
        ('transformation', '转换规则'),
        ('enrichment', '丰富规则'),
    ]

    # 规则信息
    rule_name = models.CharField(max_length=200, verbose_name="规则名称", unique=True)
    description = models.TextField(verbose_name="规则描述", blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE, verbose_name="规则类型")

    # 规则配置
    field_name = models.CharField(max_length=100, verbose_name="字段名称")
    condition = models.JSONField(verbose_name="条件配置", help_text="JSON格式的条件配置")
    action = models.JSONField(verbose_name="执行动作", help_text="JSON格式的动作配置")

    # 适用条件
    applicable_models = models.JSONField(verbose_name="适用模型", default=list)
    priority = models.IntegerField(verbose_name="优先级", default=0)

    # 系统信息
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "数据清洗规则"
        verbose_name_plural = "数据清洗规则"
        ordering = ['priority', '-created_at']

    def __str__(self):
        return self.rule_name


class DataQualityReport(models.Model):
    """数据质量报告模型"""
    QUALITY_STATUS = [
        ('excellent', '优秀'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差'),
        ('bad', '很差'),
    ]

    # 报告信息
    report_period = models.CharField(max_length=50, verbose_name="报告周期",
                                     help_text="例如：2024年第一季度")
    report_date = models.DateField(verbose_name="报告日期")

    # 质量指标
    completeness_score = models.FloatField(verbose_name="完整性得分", default=0)
    accuracy_score = models.FloatField(verbose_name="准确性得分", default=0)
    consistency_score = models.FloatField(verbose_name="一致性得分", default=0)
    timeliness_score = models.FloatField(verbose_name="及时性得分", default=0)
    overall_score = models.FloatField(verbose_name="综合得分", default=0)
    quality_status = models.CharField(max_length=20, choices=QUALITY_STATUS, verbose_name="质量状态")

    # 详细统计
    total_records = models.IntegerField(verbose_name="总记录数", default=0)
    complete_records = models.IntegerField(verbose_name="完整记录数", default=0)
    accurate_records = models.IntegerField(verbose_name="准确记录数", default=0)
    error_records = models.IntegerField(verbose_name="错误记录数", default=0)

    # 问题详情
    issues_summary = models.JSONField(verbose_name="问题摘要", default=dict)
    improvement_suggestions = models.TextField(verbose_name="改进建议", blank=True)

    # 系统信息
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="生成人")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="生成时间")

    class Meta:
        verbose_name = "数据质量报告"
        verbose_name_plural = "数据质量报告"
        ordering = ['-report_date']

    def __str__(self):
        return f"数据质量报告 - {self.report_period}"