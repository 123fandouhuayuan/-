from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import os


class ReportConfig(AppConfig):
    """报告生成应用配置"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.report'
    verbose_name = _('报告管理')
    icon = 'fas fa-file-alt'
    description = _('生成、管理和分发评价报告')

    # 报告生成配置
    report_formats = ['docx', 'pdf', 'xlsx', 'html']
    default_template = 'standard_report.docx'
    report_cache_days = 7  # 报告缓存保留天数
    max_concurrent_generations = 3  # 最大并发生成数量

    def ready(self):
        """
        应用准备好时执行
        注意：避免在ready()中直接访问数据库
        """
        # 导入信号处理器（如果有）
        try:
            import apps.report.signals
        except ImportError:
            pass

        print(f"{self.verbose_name} 应用已加载")

    def create_report_directories(self):
        """
        创建报告相关的目录结构（需要在初始化后调用）
        这个方法不要放在ready()中
        """
        from django.conf import settings

        directories = [
            os.path.join(settings.MEDIA_ROOT, 'report_templates'),
            os.path.join(settings.MEDIA_ROOT, 'generated_reports'),
            os.path.join(settings.MEDIA_ROOT, 'report_cache'),
            os.path.join(settings.MEDIA_ROOT, 'temp_reports'),
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"创建报告目录: {directory}")

    def initialize_default_templates(self):
        """
        初始化默认报告模板（需要在数据库迁移后手动调用）
        这个方法不要放在ready()中
        """
        try:
            from .models import ReportTemplate
            import uuid

            default_templates = [
                {
                    'name': '标准评价报告模板',
                    'description': '包含所有评价维度的标准报告模板',
                    'template_type': 'evaluation',
                    'format_type': 'word',
                    'variables': ['machine_info', 'evaluation_scores', 'radar_chart', 'recommendations'],
                    'sections': ['封面', '摘要', '详细分析', '附录'],
                    'is_default': True,
                },
            ]

            for template_data in default_templates:
                # 检查是否已存在同名模板
                if not ReportTemplate.objects.filter(name=template_data['name']).exists():
                    try:
                        # 创建模板实例（不包含实际文件）
                        ReportTemplate.objects.create(
                            template_id=uuid.uuid4(),
                            **template_data
                        )
                        print(f"创建报告模板: {template_data['name']}")
                    except Exception as e:
                        print(f"创建模板 {template_data['name']} 失败: {e}")

        except Exception as e:
            print(f"初始化默认模板时出错: {e}")

    def get_report_formats_info(self):
        """
        获取支持的报告格式信息
        """
        return {
            'docx': {
                'name': 'Word文档',
                'extension': '.docx',
                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'description': '可编辑的Word文档格式',
            },
            'pdf': {
                'name': 'PDF文档',
                'extension': '.pdf',
                'mime_type': 'application/pdf',
                'description': '便携式文档格式，适合打印',
            },
            'xlsx': {
                'name': 'Excel文件',
                'extension': '.xlsx',
                'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'description': '包含详细数据的Excel文件',
            },
            'html': {
                'name': '网页格式',
                'extension': '.html',
                'mime_type': 'text/html',
                'description': '可在浏览器中查看的网页格式',
            },
        }

    def validate_template_file(self, template_file):
        """
        验证报告模板文件
        返回验证结果和错误信息
        """
        import os
        from django.core.exceptions import ValidationError

        # 检查文件扩展名
        allowed_extensions = ['.docx', '.dotx', '.pdf', '.html']
        ext = os.path.splitext(template_file.name)[1].lower()

        if ext not in allowed_extensions:
            raise ValidationError(f"不支持的模板文件格式。支持格式: {', '.join(allowed_extensions)}")

        # 检查文件大小（最大10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        if template_file.size > max_size:
            raise ValidationError(f"模板文件过大。最大允许大小: {max_size // (1024 * 1024)}MB")

        return True