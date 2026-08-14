"""
URL configuration for qms_evaluation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('data/', include('apps.data_management.urls')),
    path('evaluation/', include('apps.evaluation.urls')),
    path('reports/', include('apps.report.urls')),
    path('visualization/', include('apps.visualization.urls')),
    path('system/', include('apps.system.urls')),
    
    # 达梦数据库API路由
    path('dameng/', include('apps.data_management.urls_dameng')),

    path('dashboard/', RedirectView.as_view(url='/visualization/', permanent=True)),

    path('', RedirectView.as_view(url='/accounts/login/')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))