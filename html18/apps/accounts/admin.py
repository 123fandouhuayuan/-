from django.contrib import admin
from .models import UserProfile, AdminKey


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'company', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'company']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminKey)
class AdminKeyAdmin(admin.ModelAdmin):
    list_display = ['key', 'status', 'used_count', 'max_uses', 'expires_at', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['key', 'description', 'created_by__username']
    readonly_fields = ['key', 'used_count', 'created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('key', 'status', 'description')
        }),
        ('使用限制', {
            'fields': ('max_uses', 'expires_at')
        }),
        ('统计信息', {
            'fields': ('used_count', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时设置创建者
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # 编辑现有对象时，key字段只读
            readonly.append('key')
        return readonly
