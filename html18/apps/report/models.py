from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import uuid


class ReportTemplate(models.Model):
    """报告模板模型"""
    TEMPLATE_TYPES = [
        ('evaluation', '评价报告'),
        ('comparison', '对比报告'),
        ('trend', '趋势报告'),
        ('summary', '汇总报告'),
        ('certificate', '证书报告'),
    ]

    FORMAT_TYPES = [
        ('word', 'Word文档'),
        ('pdf', 'PDF文档'),
        ('html', 'HTML网页'),
        ('excel', 'Excel表格'),
    ]

    # 模板信息
    template_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="模板ID")
    name = models.CharField(max_length=200, verbose_name="模板名称", unique=True)
    description = models.TextField(verbose_name="模板描述", blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, verbose_name="模板类型")
    format_type = models.CharField(max_length=20, choices=FORMAT_TYPES, default='word', verbose_name="格式类型")

    # 模板文件
    template_file = models.FileField(upload_to='report_templates/', verbose_name="模板文件")
    preview_image = models.ImageField(upload_to='template_previews/', verbose_name="预览图", null=True, blank=True)

    # 配置信息
    variables = models.JSONField(verbose_name="模板变量", default=list,
                                 help_text="JSON数组，包含模板中可用的变量")
    sections = models.JSONField(verbose_name="报告章节", default=list,
                                help_text="JSON数组，定义报告的结构")

    # 样式配置
    styles = models.JSONField(verbose_name="样式配置", default=dict,
                              help_text="JSON格式的样式配置")

    # 系统信息
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "报告模板"
        verbose_name_plural = "报告模板"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class GeneratedReport(models.Model):
    """生成的报告模型"""
    STATUS_CHOICES = [
        ('generating', '生成中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('archived', '已归档'),
    ]

    # 报告信息
    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="报告ID")
    report_name = models.CharField(max_length=255, verbose_name="报告名称")
    report_type = models.CharField(max_length=20, verbose_name="报告类型")

    # 关联数据
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL,
                                 verbose_name="使用模板", null=True, blank=True)
    evaluation = models.ForeignKey('evaluation.Evaluation', on_delete=models.CASCADE,
                                   verbose_name="关联评价", null=True, blank=True)

    # 文件信息
    report_file = models.FileField(upload_to='generated_reports/%Y/%m/%d/', verbose_name="报告文件")
    file_format = models.CharField(max_length=10, verbose_name="文件格式")
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)")

    # 生成信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating', verbose_name="状态")
    generation_parameters = models.JSONField(verbose_name="生成参数", default=dict)

    # 错误信息
    error_message = models.TextField(verbose_name="错误信息", blank=True)
    error_details = models.JSONField(verbose_name="错误详情", null=True, blank=True)

    # 统计信息
    page_count = models.IntegerField(verbose_name="页数", default=0)
    chart_count = models.IntegerField(verbose_name="图表数量", default=0)
    table_count = models.IntegerField(verbose_name="表格数量", default=0)

    # 系统信息
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="生成人")
    generation_time = models.DateTimeField(auto_now_add=True, verbose_name="生成时间")
    completed_time = models.DateTimeField(verbose_name="完成时间", null=True, blank=True)
    download_count = models.IntegerField(verbose_name="下载次数", default=0)

    class Meta:
        verbose_name = "生成报告"
        verbose_name_plural = "生成报告"
        ordering = ['-generation_time']

    def __str__(self):
        return f"{self.report_name} ({self.get_status_display()})"


class ReportSchedule(models.Model):
    """报告计划模型"""
    FREQUENCY_CHOICES = [
        ('daily', '每日'),
        ('weekly', '每周'),
        ('monthly', '每月'),
        ('quarterly', '每季度'),
        ('yearly', '每年'),
        ('custom', '自定义'),
    ]

    STATUS_CHOICES = [
        ('active', '激活'),
        ('paused', '暂停'),
        ('completed', '完成'),
        ('failed', '失败'),
    ]

    # 计划信息
    schedule_name = models.CharField(max_length=200, verbose_name="计划名称", unique=True)
    description = models.TextField(verbose_name="计划描述", blank=True)

    # 计划配置
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name="报告模板")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="频率")
    custom_cron = models.CharField(max_length=100, verbose_name="自定义Cron表达式", blank=True)

    # 数据筛选
    data_filters = models.JSONField(verbose_name="数据筛选条件", default=dict)
    recipient_emails = models.JSONField(verbose_name="收件人邮箱", default=list)

    # 执行配置
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期", null=True, blank=True)
    next_run = models.DateTimeField(verbose_name="下次运行时间", null=True, blank=True)
    last_run = models.DateTimeField(verbose_name="上次运行时间", null=True, blank=True)

    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="状态")
    total_runs = models.IntegerField(verbose_name="总运行次数", default=0)
    successful_runs = models.IntegerField(verbose_name="成功次数", default=0)
    failed_runs = models.IntegerField(verbose_name="失败次数", default=0)

    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "报告计划"
        verbose_name_plural = "报告计划"
        ordering = ['next_run', '-created_at']

    def __str__(self):
        return f"{self.schedule_name} ({self.get_frequency_display()})"