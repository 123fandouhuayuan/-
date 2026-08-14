from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import importlib


class EvaluationConfig(AppConfig):
    """质量评价应用配置"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.evaluation'
    verbose_name = _('质量评价')
    icon = 'fas fa-chart-line'
    description = _('执行机床质量评价、权重计算和结果分析')

    # 评价算法配置
    algorithms = {
        'ahp': {
            'name': '层次分析法',
            'module': 'algorithms.ahp',
            'class_name': 'AHPCalculator',
            'description': '基于专家判断的层次分析法',
        },
        'entropy': {
            'name': '信息熵法',
            'module': 'algorithms.entropy',
            'class_name': 'EntropyCalculator',
            'description': '基于数据离散度的信息熵法',
        },
        'combined': {
            'name': '组合赋权法',
            'module': 'algorithms.combined',
            'class_name': 'CombinedWeightCalculator',
            'description': 'AHP与信息熵组合赋权',
        },

    }

    # 权重方案配置
    weight_schemes = {
        'general': {
            'name': '通用型',
            'weights': {
                'accuracy': 0.2,
                'reliability': 0.2,
                'performance': 0.2,
                'intelligence': 0.2,
                'green': 0.2,
            }
        },
        'high_precision': {
            'name': '高精型',
            'weights': {
                'accuracy': 0.4,
                'reliability': 0.2,
                'performance': 0.15,
                'intelligence': 0.15,
                'green': 0.1,
            }
        },
        'high_reliability': {
            'name': '高可靠型',
            'weights': {
                'accuracy': 0.15,
                'reliability': 0.4,
                'performance': 0.15,
                'intelligence': 0.15,
                'green': 0.15,
            }
        },
    }

    def ready(self):
        """
        应用准备好时执行
        """
        # 导入信号处理器（如果有）
        try:
            import apps.evaluation.signals
        except ImportError:
            pass

        print(f"{self.verbose_name} 应用已加载")

    def initialize_algorithms(self):
        """
               初始化评价算法模块（需要手动调用）
               这个方法不要放在ready()中
               """
        self.algorithm_instances = {}

        for algo_id, algo_info in self.algorithms.items():
            try:
                # 动态导入算法模块
                module_path = f"apps.evaluation.{algo_info['module']}"
                module = importlib.import_module(module_path)

                # 获取算法类
                algo_class = getattr(module, algo_info['class_name'])

                # 创建算法实例
                self.algorithm_instances[algo_id] = algo_class()

                print(f"加载算法: {algo_info['name']}")

            except (ImportError, AttributeError) as e:
                print(f"加载算法 {algo_id} 失败: {e}")
                # 创建占位算法实例
                self.algorithm_instances[algo_id] = None

    def create_default_templates(self):
        """
        创建默认的评价模板（需要在数据库迁移后手动调用）
        这个方法不要放在ready()中
        """
        try:
            from .models import EvaluationTemplate

            default_templates = [
                {
                    'name': '标准机床评价模板',
                    'description': '适用于大多数机床的标准评价模板',
                    'applicable_machine_types': ['milling', 'boring', 'machining_center', 'lathe'],
                },
            ]

            for template_data in default_templates:
                template, created = EvaluationTemplate.objects.get_or_create(
                    name=template_data['name'],
                    defaults=template_data
                )
                if created:
                    print(f"创建评价模板: {template.name}")

        except Exception as e:
            print(f"创建默认模板时出错: {e}")