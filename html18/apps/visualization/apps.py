from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import json


class VisualizationConfig(AppConfig):
    """可视化分析应用配置"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.visualization'
    verbose_name = _('可视化分析')
    icon = 'fas fa-chart-bar'
    description = _('提供数据可视化、图表展示和仪表板功能')

    # 可视化配置
    chart_types = ['line', 'bar', 'pie', 'radar', 'scatter', 'heatmap']
    default_theme = 'light'
    max_data_points = 10000  # 最大数据点数量
    cache_timeout = 300  # 缓存超时时间（秒）

    # 图表颜色方案
    color_schemes = {
        'default': ['#2E93fA', '#66DA26', '#546E7A', '#E91E63', '#FF9800'],
        'pastel': ['#A7C6ED', '#B5EAD7', '#FFDAC1', '#FFB7B2', '#E2F0CB'],
        'vibrant': ['#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0', '#118AB2'],
    }

    def ready(self):
        """
        应用准备好时执行
        注意：避免在ready()中直接访问数据库
        """
        # 导入信号处理器（如果有）
        try:
            import apps.visualization.signals
        except ImportError:
            pass

        # 预加载可视化模板（无数据库访问）
        self.preload_templates()

        print(f"{self.verbose_name} 应用已加载")

    def initialize_default_dashboards(self):
        """
        初始化默认仪表板（需要在数据库迁移后手动调用）
        这个方法不要放在ready()中
        """
        try:
            from .models import Dashboard

            default_dashboards = [
                {
                    'name': '质量评价概览',
                    'description': '显示质量评价的关键指标和趋势',
                    'layout_type': 'grid',
                    'layout_config': {'columns': 3, 'rows': 2},
                    'theme': 'light',
                    'is_public': True,
                },
            ]

            for dashboard_data in default_dashboards:
                if not Dashboard.objects.filter(name=dashboard_data['name']).exists():
                    try:
                        Dashboard.objects.create(**dashboard_data)
                        print(f"创建默认仪表板: {dashboard_data['name']}")
                    except Exception as e:
                        print(f"创建仪表板 {dashboard_data['name']} 失败: {e}")

        except Exception as e:
            print(f"初始化默认仪表板时出错: {e}")

    def preload_templates(self):
        """
        预加载可视化模板（无数据库访问）
        """
        self.visualization_templates = {}

        default_templates = {
            'score_distribution': {
                'name': '得分分布图',
                'chart_type': 'bar',
                'config': {
                    'xAxis': {'type': 'category', 'name': '得分区间'},
                    'yAxis': {'type': 'value', 'name': '数量'},
                    'series': [{'type': 'bar'}],
                }
            },
            'radar_comparison': {
                'name': '雷达对比图',
                'chart_type': 'radar',
                'config': {
                    'radar': {
                        'indicator': [
                            {'name': '精度', 'max': 100},
                            {'name': '可靠性', 'max': 100},
                            {'name': '性能', 'max': 100},
                            {'name': '智能化', 'max': 100},
                            {'name': '绿色化', 'max': 100},
                        ]
                    },
                    'series': [{'type': 'radar'}],
                }
            },
        }

        self.visualization_templates.update(default_templates)

    def get_template(self, template_name):
        """
        获取可视化模板
        """
        return self.visualization_templates.get(template_name)

    def get_all_templates(self):
        """
        获取所有可视化模板
        """
        return self.visualization_templates

    def create_chart_from_template(self, template_name, data, custom_config=None):
        """
        根据模板创建图表配置
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"模板 {template_name} 不存在")

        # 复制模板配置
        chart_config = json.loads(json.dumps(template['config']))

        # 应用数据
        if 'series' in chart_config and data:
            for series in chart_config['series']:
                series['data'] = data

        # 应用自定义配置
        if custom_config:
            chart_config.update(custom_config)

        return chart_config

    def validate_chart_data(self, data, chart_type):
        """
        验证图表数据是否符合要求
        """
        if not data:
            return False, "数据不能为空"

        if chart_type == 'line' and len(data) > self.max_data_points:
            return False, f"数据点过多。最大允许数量: {self.max_data_points}"

        # 根据图表类型进行验证
        if chart_type in ['pie', 'radar']:
            if not isinstance(data, list):
                return False, "数据必须是列表格式"

        return True, "数据验证通过"

    def get_color_scheme(self, scheme_name='default'):
        """
        获取颜色方案
        """
        return self.color_schemes.get(scheme_name, self.color_schemes['default'])