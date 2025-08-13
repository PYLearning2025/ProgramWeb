from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib import messages
from functools import wraps
from .models import FeatureToggle

def feature_required(feature_name):
    """
    功能開關裝飾器 - 檢查功能是否啟用
    
    Args:
        feature_name (str): 功能名稱
        redirect_url (str): 重導向URL，如果為None則顯示自訂錯誤頁面
        message (str): 停用時顯示的訊息
        status_code (int): 回傳的HTTP狀態碼，預設為403 (Forbidden)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 管理員不受功能開關限制
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            if FeatureToggle.is_feature_enabled(feature_name):
                return view_func(request, *args, **kwargs)
            else:
                return render(request, 'errors/403.html', status=403)
        return _wrapped_view
    return decorator

def admin_only(view_func):
    """
    管理員專用裝飾器 - 檢查用戶是否為管理員
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'errors/403.html', status=403)
    return _wrapped_view
