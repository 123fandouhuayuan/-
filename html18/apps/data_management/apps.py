from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import os


class DataManagementConfig(AppConfig):
    """数据管理应用配置"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data_management'
    verbose_name = _('数据管理')
    icon = 'fas fa-database'
    description = _('管理机床数据、数据导入导出和数据清洗')

    # 数据管理特定配置
    allowed_import_formats = ['xlsx', 'xls', 'csv', 'json']
    max_upload_size_mb = 50  # 最大上传文件大小（MB）
    backup_directory = 'data_backups'  # 数据备份目录
    cleanup_days = 30  # 自动清理30天前的临时文件

    def ready(self):
        """
        应用准备好时执行
        注意：避免在ready()中直接访问数据库
        """
        # 导入信号处理器（如果有）
        try:
            import apps.data_management.signals
        except ImportError:
            pass

        print(f"{self.verbose_name} 应用已加载")

    def initialize_validation_rules(self):
        """
        初始化数据验证规则（需要在数据库迁移后手动调用）
        这个方法不要放在ready()中
        """
        try:
            from .models import DataCleaningRule

            # 这里可以添加初始化验证规则的代码
            print("初始化数据管理验证规则...")

        except Exception as e:
            print(f"初始化验证规则时出错: {e}")

    def get_import_formats_info(self):
        """
        获取支持的导入格式信息
        返回格式列表和对应的MIME类型
        """
        return {
            'xlsx': {
                'name': 'Excel工作簿',
                'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'extensions': ['.xlsx'],
            },
            'xls': {
                'name': 'Excel 97-2003工作簿',
                'mime_type': 'application/vnd.ms-excel',
                'extensions': ['.xls'],
            },
            'csv': {
                'name': '逗号分隔值文件',
                'mime_type': 'text/csv',
                'extensions': ['.csv'],
            },
            'json': {
                'name': 'JSON数据文件',
                'mime_type': 'application/json',
                'extensions': ['.json'],
            },
        }

    def get_export_formats_info(self):
        """
        获取支持的导出格式信息
        """
        return {
            'excel': {
                'name': 'Excel文件',
                'format': 'xlsx',
                'description': '包含多个工作表的Excel文件',
            },
            'csv': {
                'name': 'CSV文件',
                'format': 'csv',
                'description': '逗号分隔的文本文件',
            },
            'pdf': {
                'name': 'PDF文档',
                'format': 'pdf',
                'description': '便携式文档格式',
            },
            'json': {
                'name': 'JSON数据',
                'format': 'json',
                'description': 'JavaScript对象表示法',
            },
        }