from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .decorators import admin_required


def register(request):
    """用户注册"""
    # 如果用户已经登录，直接跳转到仪表板
    if request.user.is_authenticated:
        return redirect('evaluation_dashboard')

    from .forms import CustomUserCreationForm
    from .models import UserProfile, AdminKey

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        role = request.POST.get('role', 'user')
        company = request.POST.get('company', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        admin_key = request.POST.get('admin_key', '')
        
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # 如果是管理员或专家角色，使用管理员密钥
            if role in ('admin', 'expert') and admin_key:
                try:
                    key_obj = AdminKey.objects.get(key=admin_key)
                    if key_obj.is_valid():
                        key_obj.use()  # 使用密钥
                except AdminKey.DoesNotExist:
                    pass  # 表单验证已经处理了这种情况
            
            # 根据角色设置用户权限
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            
            # 创建UserProfile
            UserProfile.objects.create(
                user=user,
                role=role,
                company=company,
                phone=phone,
                email=email
            )
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'账户 {username} 创建成功！')
                
                # 简化实现，直接跳转到评价仪表板
                return redirect('evaluation_dashboard')
    else:
        form = CustomUserCreationForm()

    context = {
        'title': '用户注册',
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


@csrf_protect
def user_login(request):
    """用户登录"""
    if request.user.is_authenticated:
        return redirect('evaluation_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        captcha_code = request.POST.get('captcha_code', '').strip()

        if not captcha_code:
            from django.contrib import messages
            messages.error(request, '请输入图片验证码')
            context = {
                'title': '用户登录',
                'form': form
            }
            return render(request, 'accounts/login.html', context)

        session_key = request.session.session_key
        if session_key:
            from .models import LoginCaptcha
            is_valid = LoginCaptcha.verify(session_key, captcha_code)
            if not is_valid:
                from django.contrib import messages
                messages.error(request, '图片验证码错误，请重新输入')
                context = {
                    'title': '用户登录',
                    'form': form,
                    'username': request.POST.get('username', ''),
                    'password': request.POST.get('password', ''),
                    'captcha_code': request.POST.get('captcha_code', '')
                }
                return render(request, 'accounts/login.html', context)

        if form.is_valid():
            user = form.get_user()

            remember_me = request.POST.get('remember_me', False)
            if remember_me:
                request.session.set_expiry(14 * 24 * 60 * 60)
            else:
                request.session.set_expiry(0)

            login(request, user)
            from django.contrib import messages
            messages.success(request, f'欢迎回来，{user.username}！')

            return redirect('evaluation_dashboard')
        else:
            from django.contrib.auth.models import User
            username = request.POST.get('username', '')
            try:
                User.objects.get(username=username)
                request.session['login_error_type'] = 'password_error'
            except User.DoesNotExist:
                request.session['login_error_type'] = 'user_not_exists'
    else:
        form = AuthenticationForm()
        if 'login_error_type' in request.session:
            del request.session['login_error_type']

    context = {
        'title': '用户登录',
        'form': form
    }
    return render(request, 'accounts/login.html', context)


@login_required
def profile(request):
    """用户资料"""
    from .models import UserProfile
    
    try:
        user_profile = request.user.userprofile
        has_profile = True
    except UserProfile.DoesNotExist:
        user_profile = None
        has_profile = False
    
    # 获取用户基本信息，避免触发权限查询
    user_info = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'date_joined': request.user.date_joined,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
        'is_authenticated': True,  # 添加此属性以支持 base.html 的检查
    }

    context = {
        'title': '个人资料',
        'user': user_info,
        'user_profile': user_profile,
        'has_profile': has_profile
    }
    
    return render(request, 'accounts/profile.html', context)


@admin_required
def admin_key_management(request):
    """管理员密钥管理"""
    from .models import AdminKey
    from django.utils import timezone
    from datetime import timedelta
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            # 生成新密钥
            max_uses = request.POST.get('max_uses')
            expires_days = request.POST.get('expires_days')
            description = request.POST.get('description', '')
            
            # 创建新密钥
            key = AdminKey.generate_key()
            expires_at = None
            if expires_days:
                expires_at = timezone.now() + timedelta(days=int(expires_days))
            
            max_uses_int = int(max_uses) if max_uses else None
            
            AdminKey.objects.create(
                key=key,
                max_uses=max_uses_int,
                expires_at=expires_at,
                description=description,
                created_by=request.user
            )
            messages.success(request, f'管理员密钥 {key} 生成成功！')
        
        elif action == 'revoke':
            # 撤销密钥
            key_id = request.POST.get('key_id')
            try:
                key_obj = AdminKey.objects.get(id=key_id)
                key_obj.status = 'revoked'
                key_obj.save()
                messages.success(request, f'密钥 {key_obj.key} 已撤销')
            except AdminKey.DoesNotExist:
                messages.error(request, '密钥不存在')
        
        elif action == 'delete':
            # 删除密钥
            key_id = request.POST.get('key_id')
            try:
                key_obj = AdminKey.objects.get(id=key_id)
                key_obj.delete()
                messages.success(request, f'密钥 {key_obj.key} 已删除')
            except AdminKey.DoesNotExist:
                messages.error(request, '密钥不存在')
    
    # 获取所有密钥
    keys = AdminKey.objects.all().order_by('-created_at')
    
    context = {
        'title': '管理员密钥管理',
        'keys': keys,
    }
    return render(request, 'accounts/admin_key_management.html', context)


@login_required
def edit_profile(request):
    """编辑个人资料"""
    from .models import UserProfile
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, '用户资料不存在')
        return redirect('profile')
    
    if request.method == 'POST':
        company = request.POST.get('company', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        
        # 更新UserProfile
        user_profile.company = company
        user_profile.phone = phone
        user_profile.email = email
        user_profile.save()
        
        # 更新User的邮箱
        request.user.email = email
        request.user.save()
        
        messages.success(request, '个人资料更新成功！')
        return redirect('profile')
    
    context = {
        'title': '编辑个人资料',
        'user_profile': user_profile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password(request):
    """修改密码"""
    from django.contrib.auth import update_session_auth_hash
    import re
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # 验证旧密码
        if not request.user.check_password(old_password):
            messages.error(request, '旧密码不正确，请重新输入')
            return redirect('change_password')
        
        # 验证新密码长度
        if len(new_password1) < 8:
            messages.error(request, '新密码长度不能少于8个字符')
            return redirect('change_password')
        
        # 验证新密码强度
        has_upper = re.search(r'[A-Z]', new_password1) is not None
        has_lower = re.search(r'[a-z]', new_password1) is not None
        has_digit = re.search(r'[0-9]', new_password1) is not None
        has_special = re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', new_password1) is not None
        
        if not (has_upper and has_lower and has_digit and has_special):
            messages.error(request, '新密码强度不足，必须包含：大写字母、小写字母、数字和特殊字符')
            return redirect('change_password')
        
        # 验证新密码与旧密码不同
        if old_password == new_password1:
            messages.error(request, '新密码不能与旧密码相同')
            return redirect('change_password')
        
        # 验证两次输入的新密码一致
        if new_password1 != new_password2:
            messages.error(request, '两次输入的新密码不一致')
            return redirect('change_password')
        
        # 更新密码
        request.user.set_password(new_password1)
        request.user.save()
        
        # 更新会话
        update_session_auth_hash(request, request.user)
        
        messages.success(request, '密码修改成功！请使用新密码重新登录')
        return redirect('login')
    
    context = {
        'title': '修改密码',
    }
    return render(request, 'accounts/change_password.html', context)


def password_reset_view(request):
    """自定义密码重置页面（分步式）"""
    if request.user.is_authenticated:
        return redirect('evaluation_dashboard')
    
    context = {
        'title': '忘记密码',
    }
    return render(request, 'accounts/password_reset.html', context)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import re


@csrf_exempt
@require_http_methods(["POST"])
def send_verification_code(request):
    """发送邮箱验证码API"""
    email = request.POST.get('email', '').strip()
    purpose = request.POST.get('purpose', 'register').strip()

    if not email:
        return JsonResponse({'success': False, 'message': '请输入邮箱地址'})

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return JsonResponse({'success': False, 'message': '邮箱格式不正确'})

    # 密码重置时验证邮箱是否已注册
    if purpose == 'password_reset':
        from django.contrib.auth.models import User
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '该邮箱未注册，请检查后重试'})

    from .models import EmailVerificationCode
    from django.utils import timezone

    latest = EmailVerificationCode.objects.filter(email=email, purpose=purpose, is_used=False).order_by('-created_at').first()

    if latest:
        time_since_created = (timezone.now() - latest.created_at).total_seconds()
        if time_since_created < 60:
            remaining_seconds = int(60 - time_since_created)
            return JsonResponse({
                'success': False,
                'message': f'验证码已发送，请等待 {remaining_seconds} 秒后再试'
            })

        if latest.expires_at > timezone.now():
            return JsonResponse({
                'success': True,
                'message': f'验证码已发送到 {email}，请查收'
            })

    try:
        verification = EmailVerificationCode.send_verification_email(email, purpose=purpose)
        return JsonResponse({
            'success': True,
            'message': f'验证码已发送到 {email}，请查收'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'发送失败，请稍后重试'
        })


@csrf_exempt
@require_http_methods(["POST"])
def verify_reset_code(request):
    """验证密码重置验证码API"""
    email = request.POST.get('email', '').strip()
    code = request.POST.get('code', '').strip()

    if not email or not code:
        return JsonResponse({'success': False, 'message': '请输入邮箱和验证码'})

    from .models import EmailVerificationCode
    from django.utils import timezone

    verification = EmailVerificationCode.objects.filter(
        email=email,
        code=code,
        purpose='password_reset',
        is_used=False
    ).order_by('-created_at').first()

    if not verification:
        return JsonResponse({'success': False, 'message': '验证码错误'})

    if not verification.is_valid():
        return JsonResponse({'success': False, 'message': '验证码已过期，请重新获取'})

    # 标记验证码为已验证（但不标记为已使用，等密码重置成功后再标记）
    return JsonResponse({'success': True, 'message': '验证码正确'})


@csrf_exempt
@require_http_methods(["POST"])
def reset_password_with_code(request):
    """通过验证码重置密码API"""
    email = request.POST.get('email', '').strip()
    code = request.POST.get('code', '').strip()
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')

    if not email or not code or not new_password1 or not new_password2:
        return JsonResponse({'success': False, 'message': '请填写所有必填项'})

    # 验证验证码
    from .models import EmailVerificationCode
    verification = EmailVerificationCode.objects.filter(
        email=email,
        code=code,
        purpose='password_reset',
        is_used=False
    ).order_by('-created_at').first()

    if not verification:
        return JsonResponse({'success': False, 'message': '验证码错误，请重新获取'})

    if not verification.is_valid():
        return JsonResponse({'success': False, 'message': '验证码已过期，请重新获取'})

    # 验证密码复杂度
    if len(new_password1) < 8:
        return JsonResponse({'success': False, 'message': '密码长度不能少于8个字符'})

    has_upper = re.search(r'[A-Z]', new_password1) is not None
    has_lower = re.search(r'[a-z]', new_password1) is not None
    has_digit = re.search(r'[0-9]', new_password1) is not None
    has_special = re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', new_password1) is not None

    if not (has_upper and has_lower and has_digit and has_special):
        return JsonResponse({'success': False, 'message': '密码强度不足，必须包含大写字母、小写字母、数字和特殊字符'})

    if new_password1 != new_password2:
        return JsonResponse({'success': False, 'message': '两次输入的密码不一致'})

    # 查找用户并重置密码
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': '该邮箱未注册'})

    user.set_password(new_password1)
    user.save()

    # 标记验证码为已使用
    verification.use()

    return JsonResponse({'success': True, 'message': '密码重置成功，请使用新密码登录'})


def get_login_captcha(request):
    """获取登录验证码图片"""
    from django.http import HttpResponse
    from .models import LoginCaptcha
    from .captcha import generate_captcha_with_code
    import uuid

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    ip_address = request.META.get('REMOTE_ADDR')

    captcha = LoginCaptcha.create_captcha(session_key, ip_address)

    image_bytes = generate_captcha_with_code(captcha.code)

    request.session['captcha_id'] = captcha.id

    return HttpResponse(image_bytes, content_type='image/png')