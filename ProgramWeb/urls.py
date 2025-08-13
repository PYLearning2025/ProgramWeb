"""
URL configuration for ProgramWeb project.

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
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
import accounts.views as accounts_views
import userinfos.views as userinfos_views
import news.views as news_views
import questions.views as questions_views
import answers.views as answers_views
import reviews.views as reviews_views
import ai.views as ai_views
import material.views as material_views
import reports.views as reports_views
from django.conf import settings
from django.conf.urls.static import static
from userinfos.views import update_profile_img
from .views import handler400, handler403, handler404, handler500

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # -------- Accounts URLs --------
    path("", include("accounts.urls")),
    
    # -------- User Information URLs --------
    path("userinfo/", include("userinfos.urls")),
    
    # -------- News URLs --------
    path("news/", include("news.urls")),

    # -------- Questions URLs --------
    path("questions/", include("questions.urls")),

    # -------- Answers URLs --------
    path("answers/", include("answers.urls")),

    # -------- Reviews URLs --------
    path("reviews/", include("reviews.urls")),

    # -------- AI URLs --------
    path("ai/", include("ai.urls")),

    # -------- Material URLs --------
    path("material/", include("material.urls")),
    
    # -------- Reports URLs --------
    path("reports/", include("reports.urls")),

    # re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    # re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 自訂錯誤處理
handler400 = 'ProgramWeb.views.handler400'
handler403 = 'ProgramWeb.views.handler403'
handler404 = 'ProgramWeb.views.handler404'
handler500 = 'ProgramWeb.views.handler500'
