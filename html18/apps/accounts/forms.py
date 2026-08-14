from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    """自定义用户注册表单"""
    company = forms.CharField(max_length=100, required=True, label='公司名称')
    phone = forms.CharField(max_length=20, required=True, label='电话')
    email = forms.EmailField(required=True, label='联系邮箱')
    role = forms.ChoiceField(
        choices=[('user', '普通用户'), ('expert', '专家'), ('admin', '管理员')],
        required=True,
        label='用户角色',
        initial='user'
    )
    admin_key = forms.CharField(
        max_length=32,
        required=False,
        label='管理员密钥',
        widget=forms.TextInput(attrs={'placeholder': '请输入管理员密钥'})
    )
    verification_code = forms.CharField(
        max_length=6,
        required=True,
        label='邮箱验证码',
        widget=forms.TextInput(attrs={'placeholder': '请输入6位验证码', 'maxlength': '6'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'company', 'phone', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'maxlength': '50'}),
        }
    
    def __init__(self, *args, **kwargs):
        """初始化表单，设置email为必填"""
        super().__init__(*args, **kwargs)
        # 禁用默认的密码验证器
        self.fields['password1'].validators = []
        self.fields['password2'].validators = []
        # 设置email为必填并修改标签
        self.fields['email'].required = True
        self.fields['email'].label = '联系邮箱'
    
    def clean_company(self):
        """验证公司名称"""
        company = self.cleaned_data.get('company')
        if company and len(company) > 100:
            raise ValidationError("公司名称不能超过100个字符")
        return company
    
    def clean_phone(self):
        """验证电话号码"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # 简单验证：只允许数字、空格、横线、括号和加号
            import re
            if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
                raise ValidationError("电话号码格式不正确，只能包含数字、空格、横线、括号和加号")
            if len(phone) < 7:
                raise ValidationError("电话号码太短")
        return phone
    
    def clean_password1(self):
        """验证密码1"""
        password1 = self.cleaned_data.get("password1")
        
        # 验证密码长度
        if len(password1) < 8:
            raise ValidationError("您的密码必须包含至少 8 个字符")
        
        # 验证密码复杂度
        has_upper = any(c.isupper() for c in password1)
        has_lower = any(c.islower() for c in password1)
        has_digit = any(c.isdigit() for c in password1)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password1)
        
        errors = []
        if not has_upper:
            errors.append("大写字母")
        if not has_lower:
            errors.append("小写字母")
        if not has_digit:
            errors.append("数字")
        if not has_special:
            errors.append("特殊字符")
        
        if errors:
            error_msg = "您的密码必须包含：" + "、".join(errors)
            raise ValidationError(error_msg)
        
        return password1
    
    def clean_password2(self):
        """验证密码确认"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("两次输入的密码不一致")
        
        return password2
    
    def clean_username(self):
        """验证用户名"""
        username = self.cleaned_data.get("username")
        
        # 验证用户名长度
        if len(username) > 50:
            raise ValidationError("用户名不能超过50个字符")
        
        # 验证用户名是否已存在
        try:
            User.objects.get(username=username)
            raise ValidationError("该用户名已被使用")
        except User.DoesNotExist:
            pass
        
        return username
    
    def clean_admin_key(self):
        """验证管理员密钥"""
        role = self.cleaned_data.get('role')
        admin_key = self.cleaned_data.get('admin_key')
        
        # 如果选择管理员或专家角色，必须提供有效的管理员密钥
        if role in ('admin', 'expert'):
            if not admin_key:
                raise ValidationError("注册管理员或专家账号需要提供有效的管理员密钥")
            
            # 验证密钥是否存在且有效
            from .models import AdminKey
            try:
                key_obj = AdminKey.objects.get(key=admin_key)
                if not key_obj.is_valid():
                    raise ValidationError("管理员密钥已失效或已过期")
            except AdminKey.DoesNotExist:
                raise ValidationError("无效的管理员密钥")
        
        return admin_key
    
    def clean_verification_code(self):
        """验证邮箱验证码"""
        verification_code = self.cleaned_data.get('verification_code')
        email = self.cleaned_data.get('email')
        
        if not verification_code:
            raise ValidationError("请输入验证码")
        
        if not email:
            raise ValidationError("请先输入邮箱地址")
        
        from .models import EmailVerificationCode
        
        try:
            latest = EmailVerificationCode.objects.filter(
                email=email,
                code=verification_code,
                purpose='register',
                is_used=False
            ).order_by('-created_at').first()
            
            if not latest:
                raise ValidationError("验证码不正确，请重新输入")
            
            if not latest.is_valid():
                raise ValidationError("验证码已过期，请重新获取")
            
            latest.use()
            
        except EmailVerificationCode.DoesNotExist:
            raise ValidationError("验证码不正确，请重新输入")
        
        return verification_code
