from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('admin-keys/', views.admin_key_management, name='admin_key_management'),
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset-password-with-code/', views.reset_password_with_code, name='reset_password_with_code'),
    path('captcha/', views.get_login_captcha, name='login_captcha'),
    
    # 密码重置页面（自定义分步式）
    path('password_reset/', views.password_reset_view, name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/reset/done/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]