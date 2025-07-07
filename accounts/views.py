from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from accounts.forms import LoginForm, RegisterForm
from django.http import JsonResponse
from .models import Category
from userinfos.models import UserInfo
from news.models import NewsUnit
import re

# 首頁
def index(request):
    news_list = NewsUnit.objects.filter(is_published=True).order_by('-published_date')[:3]
    return render(request, 'index.html', {'news_list': news_list})

# 登入
def login(request):
    if request.user.is_authenticated:
        return redirect(reverse('Index'))

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me', False)

            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                auth_login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    # 14天的session過期時間
                    request.session.set_expiry(1209600)
                return JsonResponse({"success": True, "message": "登入成功！", "redirect_url": reverse('Index')})
            else:
                form.errors.clear()
                form.add_error(None, "沒有此帳號")
        else:
            form.errors.clear()
            form.add_error(None, "帳號或密碼錯誤")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', locals())

# 登出
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect(reverse('Index'))
    else:
        return redirect(reverse('Login'))

# 註冊
def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('Index'))

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        category_id = request.POST.get('category')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({"success": False, "message": "無效的類別選擇"})

        if form.is_valid():
            user = form.save(commit=False)
            user.category = category
            if category.id <= 5:
                # 學生身份
                student_id = form.cleaned_data['username']
                # 學號格式驗證
                if not re.match(r'^\d{9}$', student_id):
                    return JsonResponse({"success": False, "message": "學號格式錯誤，請輸入9位數字"})
                user.save()
                UserInfo.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    student_id=student_id
                )
            else:
                # 社會人士
                company = form.cleaned_data.get('company')
                job = form.cleaned_data.get('job')
                if not company or not job:
                    return JsonResponse({"success": False, "message": "公司與職稱為必填"})
                user.save()
                UserInfo.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    company=company,
                    job=job
                )
            return JsonResponse({"success": True, "message": "註冊成功！"})
        else:
            # 收集所有錯誤訊息
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{form.fields[field].label if field in form.fields else field}: {error}")
            return JsonResponse({"success": False, "message": "；".join(error_messages)})
    form = RegisterForm()
    return render(request, 'accounts/register.html', locals())