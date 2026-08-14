from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string


class UserProfile(models.Model):
    """用户资料模型 - 扩展Django User模型"""
    ROLE_CHOICES = [
        ('user', '普通用户'),
        ('expert', '专家'),
        ('admin', '管理员'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="用户角色", default='user')
    company = models.CharField(max_length=100, verbose_name="公司名称", blank=True)
    phone = models.CharField(max_length=20, verbose_name="电话", blank=True)
    email = models.EmailField(verbose_name="联系邮箱", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_expert(self):
        return self.role == 'expert'
    
    def is_user(self):
        return self.role == 'user'
    
    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"


class AdminKey(models.Model):
    """管理员密钥模型"""

    STATUS_CHOICES = [
        ('active', '有效'),
        ('expired', '已失效'),
        ('revoked', '已撤销'),
    ]

    key = models.CharField(max_length=32, unique=True, verbose_name="密钥", help_text="管理员注册密钥")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间", help_text="留空表示永不过期")
    used_count = models.IntegerField(default=0, verbose_name="使用次数")
    max_uses = models.IntegerField(null=True, blank=True, verbose_name="最大使用次数", help_text="留空表示无限制")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者", related_name='created_admin_keys')
    description = models.CharField(max_length=200, blank=True, verbose_name="描述", help_text="密钥用途说明")

    def __str__(self):
        return f"{self.key} - {self.get_status_display()}"

    @classmethod
    def generate_key(cls):
        """生成随机密钥"""
        alphabet = string.ascii_uppercase + string.digits
        key = ''.join(secrets.choice(alphabet) for _ in range(16))
        return key

    def is_valid(self):
        """检查密钥是否有效"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def use(self):
        """使用密钥"""
        if self.is_valid():
            self.used_count += 1
            if self.max_uses and self.used_count >= self.max_uses:
                self.status = 'expired'
            self.save()
            return True
        return False

    class Meta:
        verbose_name = "管理员密钥"
        verbose_name_plural = "管理员密钥"
        ordering = ['-created_at']


class LoginCaptcha(models.Model):
    """登录图片验证码模型"""
    session_key = models.CharField(max_length=64, verbose_name="会话Key")
    code = models.CharField(max_length=10, verbose_name="验证码")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    expires_at = models.DateTimeField(verbose_name="过期时间")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")

    def __str__(self):
        return f"{self.session_key} - {self.code}"

    @classmethod
    def generate_code(cls):
        """生成4位验证码"""
        alphabet = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(4))
        return code

    def is_valid(self):
        """检查验证码是否有效"""
        if self.is_used:
            return False
        if self.expires_at < timezone.now():
            return False
        return True

    def use(self):
        """使用验证码"""
        if self.is_valid():
            self.is_used = True
            self.save()
            return True
        return False

    @classmethod
    def create_captcha(cls, session_key, ip_address=None):
        """创建新的登录验证码"""
        from django.utils import timezone as dt
        code = cls.generate_code()
        expires_at = dt.now() + dt.timedelta(minutes=5)

        captcha = cls.objects.create(
            session_key=session_key,
            code=code,
            expires_at=expires_at,
            ip_address=ip_address
        )
        return captcha

    @classmethod
    def verify(cls, session_key, code, delete_after_verify=True):
        """验证验证码"""
        captcha = cls.objects.filter(
            session_key=session_key,
            code=code.upper(),
            is_used=False
        ).order_by('-created_at').first()

        if not captcha:
            return False

        if not captcha.is_valid():
            return False

        if delete_after_verify:
            captcha.use()

        return True

    class Meta:
        verbose_name = "登录验证码"
        verbose_name_plural = "登录验证码"
        ordering = ['-created_at']


class EmailVerificationCode(models.Model):
    """邮箱验证码模型"""
    email = models.EmailField(verbose_name="邮箱地址")
    code = models.CharField(max_length=6, verbose_name="验证码")
    purpose = models.CharField(max_length=20, default='register', verbose_name="用途")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    expires_at = models.DateTimeField(verbose_name="过期时间")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")

    def __str__(self):
        return f"{self.email} - {self.code} - {self.purpose}"

    @classmethod
    def generate_code(cls):
        """生成6位数字验证码"""
        alphabet = string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(6))
        return code

    def is_valid(self):
        """检查验证码是否有效"""
        if self.is_used:
            return False
        if self.expires_at < timezone.now():
            return False
        return True

    def use(self):
        """使用验证码"""
        if self.is_valid():
            self.is_used = True
            self.save()
            return True
        return False

    @classmethod
    def send_verification_email(cls, email, purpose='register'):
        """发送验证码到邮箱"""
        from django.core.mail import send_mail
        from django.conf import settings

        code = cls.generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=10)

        verification = cls.objects.create(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )

        if purpose == 'password_reset':
            subject = '密码重置验证码'
            message = f'您的密码重置验证码是：{code}，10分钟内有效。如非本人操作，请忽略此邮件。'
        else:
            subject = '注册验证码'
            message = f'您的注册验证码是：{code}，10分钟内有效。请勿将此验证码告诉他人。'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return verification

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = "邮箱验证码"
        ordering = ['-created_at']
