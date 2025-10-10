from django.shortcuts import render, redirect, get_object_or_404
import os
from django.http import JsonResponse
import google.genai as genai
from .models import Question, Card, CardRecord, AIResponse, GameLog, QuestionLog, ChallengeLog
from django.contrib.auth.decorators import login_required
from .decorators import answer_over, draw_over
import random
from django.urls import reverse
from django.db.models import F

client = genai.Client()

@login_required
@answer_over
def game(request):
    answered_questions_ids = QuestionLog.objects.filter(student=request.user, select=F('question__answer')).values_list('question_id', flat=True)
    unanswered_questions = Question.objects.exclude(id__in=answered_questions_ids)
    count = unanswered_questions.count()
    if count == 0:
        return redirect(reverse('Index'))
    else:
        question = random.choice(unanswered_questions)
    return render(request, 'game/game.html', {"question": question, "option_A": question.option_a, "option_B": question.option_b, "option_C": question.option_c, "option_D": question.option_d, "answer": question.answer})

@answer_over
@login_required
def check_answer(request):
    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        question_id = request.POST.get('question_id')
        correct_answer = Question.objects.get(id=question_id).answer
        QuestionLog.objects.create(
            student=request.user,
            question=Question.objects.get(id=question_id),
            select=selected_option
        )
        if selected_option == correct_answer:
            return JsonResponse({'result': 'correct'})
        else:
            return JsonResponse({'result': 'wrong'})
    return JsonResponse({'result': 'error', 'message': 'Invalid request method'})

@login_required
def wrong(request):
    return render(request, 'game/wrong.html')

@login_required
def draw(request):
    return render(request, 'game/draw.html')

@login_required
def result(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    return render(request, 'game/result.html', {"card_name": card.card_name, "card_description": card.card_description, "card_image_url": card.card_image.url if card.card_image else None})

@login_required
@draw_over
def draw_card(request):
    if request.method == 'POST':
        card = Card.objects.order_by('?').first()  # 隨機抽一張卡片
        CardRecord.objects.create(student=request.user, card=card)
        GameLog.objects.create(student=request.user, card=card)
        return JsonResponse({'redirect_url': f'/game/result/{card.id}/'})
    return JsonResponse({'result': 'error', 'message': 'Invalid request method'})