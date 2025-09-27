from django.shortcuts import render

def handler400(request, exception=None):
    """400 錯誤處理"""
    return render(request, 'errors/400.html', status=400)

def handler403(request, exception=None):
    """403 錯誤處理"""
    return render(request, 'errors/403.html', status=403)

def handler404(request, exception=None):
    """404 錯誤處理"""
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    """500 錯誤處理"""
    return render(request, 'errors/500.html', status=500)
