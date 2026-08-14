from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging


class SystemConfig(AppConfig):
    """系统管理应用配置"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.system'
    verbose_name = _('系统管理')
    icon = 'fas fa-cogs'
    description = _('管理系统配置、日志、备份和维护任务')

    # 系统配置
    system_name = '高端数控机床质量分级评价软件'
    version = '1.0.0'
    maintenance_mode = False
    debug_mode = False
    log_level = 'INFO'

    # 备份配置
    backup_enabled = True
    auto_backup_hour = 2  # 自动备份时间（凌晨2点）
    backup_retention_days = 30

    def ready(self):
        """
        应用准备好时执行
        注意：避免在ready()中直接访问数据库
        """
        # 导入信号处理器（如果有）
        try:
            import apps.system.signals
        except ImportError:
            pass

        print(f"{self.verbose_name} 应用已加载")
        print(f"系统名称: {self.system_name}")
        print(f"系统版本: {self.version}")

    def configure_logging(self):
        """
        配置日志系统（需要手动调用）
        这个方法不要放在ready()中
        """
        import os
        from django.conf import settings

        # 创建日志目录
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 配置日志处理器
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {asctime} {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'file': {
                    'level': self.log_level,
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(log_dir, 'system.log'),
                    'formatter': 'verbose',
                },
                'console': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['file', 'console'],
                    'level': 'INFO',
                    'propagate': True,
                },
                'system': {
                    'handlers': ['file', 'console'],
                    'level': self.log_level,
                    'propagate': False,
                },
            },
        }

        # 应用日志配置
        logging.config.dictConfig(log_config)
        self.logger = logging.getLogger('system')
        self.logger.info("日志系统已配置")

    def check_system_settings(self):
        """
        检查系统设置并创建默认值（需要在数据库迁移后手动调用）
        这个方法不要放在ready()中
        """
        try:
            from .models import SystemSetting

            default_settings = [
                {
                    'setting_key': 'SYSTEM_NAME',
                    'setting_name': '系统名称',
                    'description': '系统的显示名称',
                    'setting_type': 'general',
                    'value_type': 'string',
                    'setting_value': self.system_name,
                    'default_value': self.system_name,
                },
            ]

            for setting_data in default_settings:
                if not SystemSetting.objects.filter(setting_key=setting_data['setting_key']).exists():
                    try:
                        SystemSetting.objects.create(**setting_data)
                        print(f"创建系统设置: {setting_data['setting_name']}")
                    except Exception as e:
                        print(f"创建系统设置失败: {e}")

        except Exception as e:
            print(f"检查系统设置时出错: {e}")

    def start_background_tasks(self):
        """
        启动后台任务
        这里可以启动定时任务、监控任务等
        """
        try:
            # 检查是否启用Celery
            from django.conf import settings

            if hasattr(settings, 'CELERY_BROKER_URL'):
                # 如果有Celery配置，可以在这里启动Celery任务
                self.logger.info("检测到Celery配置，后台任务已启用")

            # 可以在这里启动其他后台任务
            # 例如：定期清理、数据同步等

        except ImportError as e:
            self.logger.warning(f"启动后台任务时出错: {e}")

    def get_system_info(self):
        """
        获取系统信息
        返回系统的基本信息字典
        """
        import platform
        import django
        from django.db import connection

        info = {
            'system_name': self.system_name,
            'version': self.version,
            'django_version': django.get_version(),
            'python_version': platform.python_version(),
            'os': platform.system(),
            'os_version': platform.release(),
            'database': connection.vendor,
            'database_version': getattr(connection, 'server_version', 'Unknown'),
            'timezone': self.timezone if hasattr(self, 'timezone') else 'UTC',
            'debug_mode': self.debug_mode,
            'maintenance_mode': self.maintenance_mode,
        }

        return info

    def is_maintenance_mode(self):
        """
        检查是否处于维护模式
        从数据库设置中读取
        """
        from .models import SystemSetting

        try:
            setting = SystemSetting.objects.get(setting_key='MAINTENANCE_MODE')
            return setting.get_value() == True
        except SystemSetting.DoesNotExist:
            return self.maintenance_mode