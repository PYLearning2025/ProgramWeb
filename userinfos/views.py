from django.shortcuts import render, redirect
from django.http import JsonResponse
from questions.models import Question, QuestionHistory
from userinfos.models import UserInfo
from .forms import UserInfoForm, UserEmailForm, ProfileImageForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
def userinfo(request):
    if not request.user.is_authenticated:
        return redirect('Login')
    if not hasattr(request.user, 'user_info'):
        request.user.user_info = UserInfo.objects.create(user=request.user)
    user_info = request.user.user_info
    if request.method == 'POST':
        info_form = UserInfoForm(request.POST, request.FILES, instance=user_info, category=request.user.category)
        email_form = UserEmailForm(request.POST, instance=request.user)
        # 判斷是否只上傳頭像
        if 'profile_img' in request.FILES and len(request.POST) <= 2:
            # 只驗證 info_form
            if info_form.is_valid():
                info_form.save()
                return JsonResponse({'success': True, 'message': '儲存成功'})
            else:
                return JsonResponse({'success': False, 'message': '儲存失敗'})
        else:
            # 一般情況兩個都驗證
            if info_form.is_valid() and email_form.is_valid():
                info_form.save()
                email_form.save()
                return JsonResponse({'success': True, 'message': '儲存成功'})
            else:
                return JsonResponse({'success': False, 'message': '儲存失敗'})
    else:
        info_form = UserInfoForm(instance=user_info, category=request.user.category)
        email_form = UserEmailForm(instance=request.user)
    return render(request, 'userinfos/userinfo.html', {
        'form': info_form,
        'email_form': email_form
    })

@require_POST
def update_profile_img(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': '未登入'})

    if not hasattr(request.user, 'user_info'):
        request.user.user_info = UserInfo.objects.create(user=request.user)
    
    user_info = request.user.user_info
    form = ProfileImageForm(request.POST, request.FILES, instance=user_info)
    if form.is_valid():
        instance = form.save()
        return JsonResponse({
            'success': True,
            'img_url': instance.profile_img.url if instance.profile_img else ''
        })
    else:
        return JsonResponse({'success': False, 'error': '表單驗證失敗'})

@login_required
def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('Login')
    
    questions = Question.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'userinfos/questions.html', locals())