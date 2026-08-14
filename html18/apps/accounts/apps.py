from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    """用户管理应用配置"""

    # 使用自定义的ID字段类型
    default_auto_field = 'django.db.models.BigAutoField'

    # 应用名称（Python路径）
    name = 'apps.accounts'

    # 在Django管理后台显示的中文名称
    verbose_name = _('用户管理')

    # 应用图标（可选，使用Font Awesome类名）
    icon = 'fas fa-users'

    # 应用描述
    description = _('管理系统的用户账户、权限和角色')

    def ready(self):
        """
        应用准备好时执行
        这里可以放置初始化代码，如信号连接等
        """
        # 导入信号处理器（如果需要）
        try:
            import apps.accounts.signals
        except ImportError:
            pass

        # 连接迁移后信号（示例）
        # post_migrate.connect(self.create_default_groups, sender=self)

        print(f"{self.verbose_name} 应用已加载")

    def create_default_groups(self, **kwargs):
        """
        创建默认用户组（如果需要）
        这个方法会在数据库迁移后自动调用
        """
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType

        # 创建默认用户组
        groups_data = [
            {
                'name': '管理员组',
                'permissions': [
                    'add_user', 'change_user', 'delete_user', 'view_user',
                    'add_group', 'change_group', 'delete_group', 'view_group',
                ]
            },
            {
                'name': '专家用户组',
                'permissions': [
                    'view_user', 'change_user', 'add_machine', 'change_machine',
                    'view_machine', 'add_evaluation', 'change_evaluation',
                    'view_evaluation', 'add_report', 'change_report',
                ]
            },
            {
                'name': '普通用户组',
                'permissions': [
                    'view_user', 'change_user', 'view_machine', 'add_evaluation',
                    'view_evaluation', 'view_report',
                ]
            },
        ]

        for group_info in groups_data:
            group, created = Group.objects.get_or_create(name=group_info['name'])
            if created:
                print(f"创建用户组: {group.name}")
                # 这里可以添加权限分配逻辑

    def get_app_models(self):
        """
        获取应用中的所有模型
        重写此方法可以自定义模型加载
        """
        return super().get_app_models()

    def get_model(self, model_name, require_ready=True):
        """
        获取应用中的特定模型
        重写此方法可以自定义模型获取
        """
        return super().get_model(model_name, require_ready)