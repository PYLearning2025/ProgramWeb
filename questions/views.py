from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Question, QuestionHistory, QuestionLog
from answers.models import Answer
from reviews.models import PeerReview
from .forms import QuestionForm, QuestionDetailForm
from features.decorators import feature_required

@login_required
@feature_required('question_create')
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            # 記錄創建問題的日誌
            QuestionLog.objects.create(
                question=question,
                user=request.user,
                action='created'
            )
            # 創建問題的歷史記錄
            history = QuestionHistory.objects.create(
                question=question,
                user=request.user,
                title=question.title,
                content=question.content,
                level=question.level,
                input_format=question.input_format,
                output_format=question.output_format,
                input_example=question.input_example,
                output_example=question.output_example,
                answer=question.answer,
                hint=question.hint,
                reference=question.reference,
                version=1
            )
            # 設置多對多關係
            history.tags.set(question.tags.all())
            history.topics.set(question.topics.all())
            return JsonResponse({'success': True, 'message': '問題創建成功！', 'redirect_url': reverse('UserinfoQuestions')})
        else:
            return JsonResponse({'success': False, 'message': '表單驗證失敗，請檢查您的輸入！'})
    else:
        form = QuestionForm(user=request.user)
    
    return render(request, 'questions/create.html', {'form': form, 'page_mode': 'create'})

def question_detail(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    # 使用表單顯示問題詳細信息
    form = QuestionDetailForm(instance=question)

    # 獲取問題的歷史記錄
    history = QuestionHistory.objects.filter(question=question).order_by('-version')

    # 獲取問題的回答
    answer = Answer.objects.filter(user=request.user, question=question).first()

    # 獲取問題的評論
    review = PeerReview.objects.filter(reviewed_question=question, reviewer=request.user).first()

    return render(request, 'questions/detail.html', locals())

@login_required
def question_version(request, question_id, version):
    try:
        question = Question.objects.get(id=question_id)
        history = QuestionHistory.objects.filter(question=question).order_by('-version')
        history_question = QuestionHistory.objects.get(question=question, version=version)
    except (Question.DoesNotExist, QuestionHistory.DoesNotExist):
        return render(request, 'errors/404.html', status=404)

    # 使用表單顯示問題歷史版本的詳細信息
    form = QuestionDetailForm(instance=history_question)

    return render(request, 'questions/detail.html', locals())

@login_required
@feature_required('question_update')
def question_update(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, user=request.user)
        # 抓取該問題的最新版本號
        history_version = QuestionHistory.objects.filter(question=question).order_by('-version').first().version
        if form.is_valid():
            updated_question = form.save()
            # 記錄更新問題的日誌
            QuestionLog.objects.create(
                question=updated_question,
                user=request.user,
                action='updated'
            )
            # 創建新的問題歷史記錄
            history = QuestionHistory.objects.create(
                question=updated_question,
                user=request.user,
                title=updated_question.title,
                content=updated_question.content,
                level=updated_question.level,
                input_format=updated_question.input_format,
                output_format=updated_question.output_format,
                input_example=updated_question.input_example,
                output_example=updated_question.output_example,
                answer=updated_question.answer,
                hint=updated_question.hint,
                reference=updated_question.reference,
                version=history_version + 1
            )
            # 設置多對多關係
            history.tags.set(updated_question.tags.all())
            history.topics.set(updated_question.topics.all())
            return JsonResponse({'success': True, 'message': '問題更新成功！', 'redirect_url': reverse('QuestionDetail', args=[question.id])})
        else:
            return JsonResponse({'success': False, 'message': '表單驗證失敗，請檢查您的輸入！'})
    else:
        form = QuestionForm(instance=question, user=request.user)

    return render(request, 'questions/create.html', {'form': form, 'question': question, 'page_mode': 'update'})

def question_list(request):
    if request.user.is_staff:
        questions = Question.objects.filter(is_active=True).order_by('-created_at')
    else:
        questions = Question.objects.filter(is_active=True, is_approved=True).order_by('-created_at')
    return render(request, 'questions/list.html', locals())