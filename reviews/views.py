from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import PeerReview
from questions.models import Question
from answers.models import Answer
from accounts.models import User
from django.contrib.auth.decorators import login_required
from .forms import PeerReviewForm

@login_required
def create_review(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answer = get_object_or_404(Answer, question=question)
    user = request.user
    # 檢查是否已經評分過
    if PeerReview.objects.filter(reviewer=user, reviewed_question=question).exists():
        messages.error(request, "你已經對此題目評分過了。You have already reviewed this question.")
        return redirect('QuestionDetail', question_id=question.id)

    if not answer:
        messages.error(request, "此題目沒有作答過，無法進行評分。This question has no answer, cannot review.")
        return redirect('QuestionDetail', question_id=question.id)

    if request.method == 'POST':
        form = PeerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = user
            review.reviewed_question = question
            review.save()
            messages.success(request, "評分成功！Review submitted successfully!")
            return redirect('QuestionDetail', question_id=question.id)
        else:
            messages.error(request, "請修正表單錯誤 Please correct the errors below.")
    else:
        form = PeerReviewForm()

    return render(request, 'reviews/review.html', locals())
