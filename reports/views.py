from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import ReportForm
from features.decorators import feature_required

@login_required
@feature_required('report_create')
def report_create(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 使用表單的 save 方法，它會處理附件
                report = form.save(user=request.user)
                
                return JsonResponse({
                    'success': True,
                    'message': '您的回報已成功提交，我們會盡快處理並回覆您。'
                })
                    
            except Exception as e:
                error_message = f'提交失敗：{str(e)}'
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
        else:
            error_message = '表單中存在錯誤，請修正後再提交。'
            return JsonResponse({
                'success': False,
                'message': error_message,
                'errors': form.errors
            })
    else:
        form = ReportForm()
    
    return render(request, 'reports/reports.html', {'form': form})