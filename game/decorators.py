from django.shortcuts import redirect
from functools import wraps
from django.urls import reverse
from .models import QuestionLog, GameLog
from datetime import datetime
from django.http import JsonResponse

def answer_over(function):
    @wraps(function)
    def decorated_view(request, *args, **kwargs):
        today = datetime.today().date()
        count = QuestionLog.objects.filter(student=request.user, timestamp__date=today).count()
        if count >= 5:
            return redirect(reverse('Index'))
        return function(request, *args, **kwargs)
    return decorated_view

def draw_over(function):
    @wraps(function)
    def decorated_view(request, *args, **kwargs):
        today = datetime.today().date()
        correct_count = len([i for i in QuestionLog.objects.filter(student=request.user, timestamp__date=today) if i.select == i.question.answer])
        count = correct_count - GameLog.objects.filter(student=request.user, timestamp__date=today).count()
        if count <= 0:
            return JsonResponse({'redirect_url': reverse('Index')})
        return function(request, *args, **kwargs)
    return decorated_view