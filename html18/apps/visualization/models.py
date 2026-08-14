from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import uuid


class Dashboard(models.Model):
    """可视化仪表板模型"""
    LAYOUT_TYPES = [
        ('grid', '网格布局'),
        ('freeform', '自由布局'),
        ('single', '单列布局'),
    ]

    # 仪表板信息
    dashboard_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="仪表板ID")
    name = models.CharField(max_length=200, verbose_name="仪表板名称")
    description = models.TextField(verbose_name="描述", blank=True)
    layout_type = models.CharField(max_length=20, choices=LAYOUT_TYPES, default='grid', verbose_name="布局类型")

    # 布局配置
    layout_config = models.JSONField(verbose_name="布局配置", default=dict)
    theme = models.CharField(max_length=50, verbose_name="主题", default='light',
                             choices=[('light', '浅色'), ('dark', '深色'), ('custom', '自定义')])

    # 分享设置
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    share_token = models.CharField(max_length=50, verbose_name="分享令牌", blank=True)
    access_password = models.CharField(max_length=100, verbose_name="访问密码", blank=True)

    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")

    class Meta:
        verbose_name = "可视化仪表板"
        verbose_name_plural = "可视化仪表板"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Chart(models.Model):
    """图表模型"""
    CHART_TYPES = [
        ('line', '折线图'),
        ('bar', '柱状图'),
        ('pie', '饼图'),
        ('radar', '雷达图'),
        ('scatter', '散点图'),
        ('heatmap', '热力图'),
        ('gauge', '仪表盘'),
        ('funnel', '漏斗图'),
        ('tree', '树状图'),
    ]

    # 图表信息
    chart_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="图表ID")
    name = models.CharField(max_length=200, verbose_name="图表名称")
    description = models.TextField(verbose_name="描述", blank=True)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, verbose_name="图表类型")

    # 数据配置
    data_source = models.CharField(max_length=200, verbose_name="数据源",
                                   help_text="例如：evaluation.Evaluation.objects.filter(...)")
    data_filters = models.JSONField(verbose_name="数据筛选", default=dict)
    data_mapping = models.JSONField(verbose_name="数据映射", default=dict)

    # 样式配置
    chart_config = models.JSONField(verbose_name="图表配置", default=dict)
    size_config = models.JSONField(verbose_name="尺寸配置", default=dict)

    # 交互配置
    interactions = models.JSONField(verbose_name="交互配置", default=list)
    tooltips = models.JSONField(verbose_name="提示配置", default=list)

    # 关联信息
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, verbose_name="所属仪表板",
                                  related_name='charts', null=True, blank=True)

    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    refresh_interval = models.IntegerField(verbose_name="刷新间隔(秒)", default=0)

    class Meta:
        verbose_name = "图表"
        verbose_name_plural = "图表"
        ordering = ['dashboard', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_chart_type_display()})"


class VisualizationTemplate(models.Model):
    """可视化模板模型"""
    # 模板信息
    name = models.CharField(max_length=200, verbose_name="模板名称", unique=True)
    description = models.TextField(verbose_name="描述", blank=True)

    # 模板配置
    chart_configs = models.JSONField(verbose_name="图表配置", default=list)
    layout_config = models.JSONField(verbose_name="布局配置", default=dict)

    # 预览信息
    preview_image = models.ImageField(upload_to='viz_template_previews/', verbose_name="预览图", null=True, blank=True)
    preview_url = models.URLField(verbose_name="预览链接", blank=True)

    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    is_system = models.BooleanField(default=False, verbose_name="是否系统模板")

    class Meta:
        verbose_name = "可视化模板"
        verbose_name_plural = "可视化模板"
        ordering = ['-is_system', '-created_at']

    def __str__(self):
        return self.name