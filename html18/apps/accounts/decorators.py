from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """管理员权限装饰器"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
            if not user_profile.is_admin():
                messages.error(request, '您没有权限访问此页面')
                return redirect('evaluation_dashboard')
        except Exception:
            messages.error(request, '用户资料不存在，请联系管理员')
            return redirect('evaluation_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def expert_required(view_func):
    """专家权限装饰器"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
            if not (user_profile.is_expert() or user_profile.is_admin()):
                messages.error(request, '您需要专家或管理员权限才能访问此页面')
                return redirect('evaluation_dashboard')
        except Exception:
            messages.error(request, '用户资料不存在，请联系管理员')
            return redirect('evaluation_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_user_queryset(queryset, user):
    """根据用户角色过滤查询集
    
    Args:
        queryset: Django查询集
        user: 当前用户对象
        
    Returns:
        过滤后的查询集
    """
    try:
        user_profile = user.userprofile
        if user_profile.is_admin():
            return queryset
        else:
            model = queryset.model
            if hasattr(model, 'created_by'):
                return queryset.filter(created_by=user)
            elif hasattr(model, 'evaluator'):
                return queryset.filter(evaluator=user)
            elif hasattr(model, 'imported_by'):
                return queryset.filter(imported_by=user)
            elif hasattr(model, 'exported_by'):
                return queryset.filter(exported_by=user)
            elif hasattr(model, 'generated_by'):
                return queryset.filter(generated_by=user)
            else:
                return queryset
    except Exception:
        model = queryset.model
        if hasattr(model, 'created_by'):
            return queryset.filter(created_by=user)
        elif hasattr(model, 'evaluator'):
            return queryset.filter(evaluator=user)
        elif hasattr(model, 'imported_by'):
            return queryset.filter(imported_by=user)
        elif hasattr(model, 'exported_by'):
            return queryset.filter(exported_by=user)
        elif hasattr(model, 'generated_by'):
            return queryset.filter(generated_by=user)
        else:
            return queryset
