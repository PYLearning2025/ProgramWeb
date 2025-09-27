from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import PeerReview
from questions.models import Question
from answers.models import Answer
from django.contrib.auth.decorators import login_required
from .forms import PeerReviewForm
from features.decorators import feature_required
import json

@login_required
@feature_required('review_create')
def review_create(request, question_id):
    user = request.user
    question = get_object_or_404(Question, id=question_id)
    answer = get_object_or_404(Answer, user=user, question=question)
    # 檢查是否已經評分過
    if PeerReview.objects.filter(reviewer=user, reviewed_question=question).exists():
        question = PeerReview.objects.get(reviewer=user, reviewed_question=question).reviewed_question
        review_obj = PeerReview.objects.get(reviewer=user, reviewed_question=question)
        already_reviewed = True
        review_data = {
            'question_accuracy_score': review_obj.question_accuracy_score,
            'complexity_score': review_obj.complexity_score,
            'practice_score': review_obj.practice_score,
            'answer_accuracy_score': review_obj.answer_accuracy_score,
            'readability_score': review_obj.readability_score,
            'question_advice': review_obj.question_advice,
            'answer_advice': review_obj.answer_advice,
        }
        review = json.dumps(review_data)
        
        return render(request, 'reviews/review.html', locals())

    if not answer:
        return redirect('QuestionDetail', question_id=question.id)

    else:
        form = PeerReviewForm()
        already_reviewed = False
        review = ""  # 確保變數存在但為空字串
        return render(request, 'reviews/review.html', locals())


@login_required
@feature_required('review_submit')
def review_submit(request, question_id):
    user = request.user
    question = get_object_or_404(Question, id=question_id)
    
    # 檢查用戶是否已經作答過這個題目
    answer = Answer.objects.filter(user=user, question=question).first()
    if not answer:
        return JsonResponse({
            'success': False,
            'message': '此題目沒有作答過，無法進行評分。This question has no answer, cannot review.'
        }, status=400)
    
    # 檢查是否已經評分過
    if PeerReview.objects.filter(reviewer=user, reviewed_question=question).exists():
        return JsonResponse({
            'success': False,
            'message': '你已經對此題目評分過了。You have already reviewed this question.'
        }, status=400)
    
    if request.method == 'POST':
        form = PeerReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.reviewer = user
                review.reviewed_question = question
                review.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '評分成功！Review submitted successfully!',
                    'redirect_url': reverse('ReviewList')
                }, status=200)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'評分提交失敗，請稍後再試。Review submission failed: {str(e)}'
                }, status=500)
        else:
            # 處理表單驗證錯誤
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            return JsonResponse({
                'success': False,
                'message': '表單驗證失敗，請檢查您的輸入。Form validation failed.',
                'errors': form.errors,
                'error_messages': error_messages
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': '只允許 POST 請求。Only POST requests are allowed.'
    }, status=405)

@login_required
def review_list(request):
    user = request.user
    
    # 獲取用戶作答過的所有題目
    questions = Question.objects.filter(answers__user=user).distinct().order_by('-created_at')
    
    # 構建模板需要的數據結構
    questions_data = []
    for question in questions:
        # 檢查用戶是否已經評分過這個題目
        has_reviewed = PeerReview.objects.filter(
            reviewer=user, 
            reviewed_question=question
        ).exists()
        
        # 構建評分URL
        review_url = reverse('CreateReview', args=[question.id])
        
        questions_data.append({
            'question': question,
            'has_reviewed': has_reviewed,
            'review_url': review_url,
            'user_answer': Answer.objects.filter(user=user, question=question).first()
        })
    
    return render(request, 'reviews/review_list.html', locals())