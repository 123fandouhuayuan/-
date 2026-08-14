from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class SystemLog(models.Model):
    """系统日志模型"""
    LOG_LEVELS = [
        ('debug', '调试'),
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
    ]

    LOG_TYPES = [
        ('system', '系统操作'),
        ('user', '用户操作'),
        ('security', '安全事件'),
        ('performance', '性能监控'),
        ('business', '业务日志'),
    ]

    # 日志信息
    log_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="日志ID")
    log_time = models.DateTimeField(auto_now_add=True, verbose_name="日志时间")
    log_level = models.CharField(max_length=20, choices=LOG_LEVELS, verbose_name="日志级别")
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, verbose_name="日志类型")

    # 日志内容
    module = models.CharField(max_length=100, verbose_name="模块名称")
    action = models.CharField(max_length=200, verbose_name="操作动作")
    message = models.TextField(verbose_name="日志消息")

    # 上下文信息
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="操作用户", null=True, blank=True)
    ip_address = models.GenericIPAddressField(verbose_name="IP地址", null=True, blank=True)
    user_agent = models.TextField(verbose_name="用户代理", blank=True)

    # 额外数据
    request_path = models.CharField(max_length=500, verbose_name="请求路径", blank=True)
    request_method = models.CharField(max_length=10, verbose_name="请求方法", blank=True)
    request_data = models.JSONField(verbose_name="请求数据", null=True, blank=True)
    response_data = models.JSONField(verbose_name="响应数据", null=True, blank=True)

    # 错误信息
    error_code = models.CharField(max_length=50, verbose_name="错误代码", blank=True)
    error_trace = models.TextField(verbose_name="错误堆栈", blank=True)

    # 性能信息
    execution_time = models.FloatField(verbose_name="执行时间(秒)", null=True, blank=True)
    memory_usage = models.FloatField(verbose_name="内存使用(MB)", null=True, blank=True)

    class Meta:
        verbose_name = "系统日志"
        verbose_name_plural = "系统日志"
        ordering = ['-log_time']
        indexes = [
            models.Index(fields=['log_time']),
            models.Index(fields=['log_level']),
            models.Index(fields=['log_type']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"[{self.log_level}] {self.module} - {self.action}"


class SystemSetting(models.Model):
    """系统设置模型"""
    SETTING_TYPES = [
        ('general', '常规设置'),
        ('evaluation', '评价设置'),
        ('report', '报告设置'),
        ('notification', '通知设置'),
        ('security', '安全设置'),
        ('performance', '性能设置'),
        ('license', '许可设置'),
    ]

    VALUE_TYPES = [
        ('string', '字符串'),
        ('integer', '整数'),
        ('float', '浮点数'),
        ('boolean', '布尔值'),
        ('json', 'JSON数据'),
        ('list', '列表'),
    ]

    # 设置信息
    setting_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="设置ID")
    setting_key = models.CharField(max_length=100, verbose_name="设置键", unique=True)
    setting_name = models.CharField(max_length=200, verbose_name="设置名称")
    description = models.TextField(verbose_name="描述", blank=True)
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, verbose_name="设置类型")
    value_type = models.CharField(max_length=20, choices=VALUE_TYPES, verbose_name="值类型")

    # 设置值
    setting_value = models.TextField(verbose_name="设置值")
    default_value = models.TextField(verbose_name="默认值")

    # 验证规则
    validation_rules = models.JSONField(verbose_name="验证规则", default=dict)
    options = models.JSONField(verbose_name="选项列表", null=True, blank=True)

    # 权限控制
    is_editable = models.BooleanField(default=True, verbose_name="是否可编辑")
    requires_restart = models.BooleanField(default=False, verbose_name="需要重启")

    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="最后更新人",
                                   related_name='updated_settings', null=True, blank=True)

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = "系统设置"
        ordering = ['setting_type', 'setting_key']

    def __str__(self):
        return f"{self.setting_name} ({self.setting_key})"

    def get_value(self):
        """根据值类型返回解析后的值"""
        if self.value_type == 'integer':
            return int(self.setting_value)
        elif self.value_type == 'float':
            return float(self.setting_value)
        elif self.value_type == 'boolean':
            return self.setting_value.lower() == 'true'
        elif self.value_type == 'json':
            import json
            return json.loads(self.setting_value)
        elif self.value_type == 'list':
            return self.setting_value.split(',')
        else:
            return self.setting_value


class BackupSchedule(models.Model):
    """备份计划模型"""
    FREQUENCY_CHOICES = [
        ('daily', '每日'),
        ('weekly', '每周'),
        ('monthly', '每月'),
        ('manual', '手动'),
    ]

    BACKUP_TYPES = [
        ('full', '完全备份'),
        ('incremental', '增量备份'),
        ('differential', '差异备份'),
    ]

    # 计划信息
    schedule_name = models.CharField(max_length=200, verbose_name="计划名称", unique=True)
    description = models.TextField(verbose_name="描述", blank=True)

    # 备份配置
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="频率")
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, verbose_name="备份类型")
    backup_path = models.CharField(max_length=500, verbose_name="备份路径")

    # 数据选择
    include_databases = models.BooleanField(default=True, verbose_name="包含数据库")
    include_media = models.BooleanField(default=True, verbose_name="包含媒体文件")
    include_static = models.BooleanField(default=False, verbose_name="包含静态文件")
    include_logs = models.BooleanField(default=False, verbose_name="包含日志文件")

    # 执行配置
    start_time = models.TimeField(verbose_name="开始时间")
    retention_days = models.IntegerField(verbose_name="保留天数", default=30)
    max_backups = models.IntegerField(verbose_name="最大备份数", default=10)

    # 状态信息
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    next_run = models.DateTimeField(verbose_name="下次运行时间", null=True, blank=True)
    last_run = models.DateTimeField(verbose_name="上次运行时间", null=True, blank=True)
    last_status = models.CharField(max_length=20, verbose_name="最后状态", blank=True)

    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "备份计划"
        verbose_name_plural = "备份计划"
        ordering = ['next_run', '-created_at']

    def __str__(self):
        return self.schedule_name


class LicenseManagement(models.Model):
    """许可管理模型"""
    LICENSE_TYPES = [
        ('machining_center', '加工中心'),
        ('boring_milling_machine', '镗铣床'),
    ]
    
    LICENSE_STATUS = [
        ('active', '激活'),
        ('inactive', '未激活'),
        ('expired', '已过期'),
        ('suspended', '已暂停'),
    ]

    # 许可信息
    license_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="许可ID")
    license_type = models.CharField(max_length=30, choices=LICENSE_TYPES, verbose_name="许可类型")
    license_name = models.CharField(max_length=200, verbose_name="许可名称")
    description = models.TextField(verbose_name="描述", blank=True)
    
    # 许可配置
    is_enabled = models.BooleanField(default=False, verbose_name="是否启用")
    status = models.CharField(max_length=20, choices=LICENSE_STATUS, default='inactive', verbose_name="许可状态")
    max_users = models.IntegerField(verbose_name="最大用户数", default=1)
    max_machines = models.IntegerField(verbose_name="最大机床数", default=10)
    
    # 有效期
    start_date = models.DateField(verbose_name="开始日期", null=True, blank=True)
    end_date = models.DateField(verbose_name="结束日期", null=True, blank=True)
    is_perpetual = models.BooleanField(default=False, verbose_name="永久许可")
    
    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "许可管理"
        verbose_name_plural = "许可管理"
        ordering = ['license_type', '-created_at']

    def __str__(self):
        return f"{self.license_name} ({self.get_license_type_display()})"

    def is_valid(self):
        """检查许可是否有效"""
        if not self.is_enabled:
            return False
        if self.status != 'active':
            return False
        if not self.is_perpetual and self.end_date and self.end_date < timezone.now().date():
            return False
        return True


class BackupLog(models.Model):
    """备份日志模型"""
    STATUS_CHOICES = [
        ('started', '已开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]

    # 备份信息
    backup_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="备份ID")
    schedule = models.ForeignKey(BackupSchedule, on_delete=models.CASCADE, verbose_name="备份计划")

    # 执行信息
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="状态")

    # 文件信息
    backup_file = models.CharField(max_length=500, verbose_name="备份文件", blank=True)
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)", default=0)
    compression_ratio = models.FloatField(verbose_name="压缩比", null=True, blank=True)

    # 统计信息
    total_files = models.IntegerField(verbose_name="总文件数", default=0)
    total_size = models.BigIntegerField(verbose_name="总大小(字节)", default=0)
    backup_duration = models.DurationField(verbose_name="备份时长", null=True, blank=True)

    # 错误信息
    error_message = models.TextField(verbose_name="错误信息", blank=True)
    error_details = models.JSONField(verbose_name="错误详情", null=True, blank=True)

    # 系统信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="执行人")

    class Meta:
        verbose_name = "备份日志"
        verbose_name_plural = "备份日志"
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.schedule.schedule_name} - {self.start_time}"