from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import AnswerForm
from questions.models import Question
from .models import Answer
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from features.decorators import feature_required

@login_required
@feature_required('answer_create')
def answer_create(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.user == question.user:
        return redirect('QuestionDetail', question_id=question_id)
    existing_answer = Answer.objects.filter(user=request.user, question_id=question_id).first()
    if existing_answer:
        question = existing_answer.question
        answer = existing_answer
        already_submitted = True
        return render(request, 'answers/answer.html', locals())
    else:
        already_submitted = False
        if request.method == 'POST':
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.user = request.user
                answer.question_id = question_id
                answer.save()
                already_submitted = True
                return render(request, 'answers/answer.html', locals())
        else:
            form = AnswerForm()
        return render(request, 'answers/answer.html', locals())

@login_required
@feature_required('answer_submit')
def answer_submit(request):
    if request.method != 'POST':
        return JsonResponse({'message': '只允許 POST 請求'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'message': '請先登入'}, status=403)
    # 檢查是否已經提交過答案
    if Answer.objects.filter(user=request.user, question_id=request.POST.get('question_id')).exists():
        answer = Answer.objects.get(user=request.user, question_id=request.POST.get('question_id'))
        return JsonResponse({'message': '您已經提交過答案', 'redirect_url': reverse('QuestionDetail', args=[answer.question_id])}, status=403)
    code = request.POST.get('code', '').strip()
    if not code:
        return JsonResponse({'message': '答案不得為空'}, status=400)
    # 這裡假設前端會帶 question_id，可根據實際需求調整
    question_id = request.POST.get('question_id')
    if not question_id:
        return JsonResponse({'message': '缺少題目編號'}, status=400)
    try:
        question = Question.objects.get(id=question_id)
        if request.user == question.user:
            return JsonResponse({'message': '您不能提交自己的答案', 'redirect_url': reverse('QuestionDetail', args=[question_id])}, status=403)
    except Question.DoesNotExist:
        return JsonResponse({'message': '題目不存在'}, status=404)
    # 檢查是否已經有答案
    answer, created = Answer.objects.get_or_create(user=request.user, question=question)
    answer.answer = code
    answer.save()
    return JsonResponse({'message': '答案已成功提交！', 'redirect_url': reverse('QuestionDetail', args=[question_id])})

def answer_debug(request):
    """實作debug功能"""
    pass