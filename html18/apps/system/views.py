from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def system_settings(request):
    """系统设置"""
    context = {
        'title': '系统管理',
        'page_title': '系统设置',
    }
    return render(request, 'system/settings.html', context)

@login_required
def logs_view(request):
    """系统日志"""
    context = {
        'title': '系统日志',
        'page_title': '系统日志查看',
    }
    return render(request, 'system/logs.html', context)