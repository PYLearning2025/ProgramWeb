from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import AnswerForm
from questions.models import Question
from .models import Answer, Transcript, Debug
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from features.decorators import feature_required
import tempfile
import os
import chardet
from judge.glottest import run_test_cases

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
    # 檢測Debug是否為AC或WA才可以提交
    code = normalize_code_encoding(code)
    
    if code is None:
        return JsonResponse({'message': '題目不存在或未獲批准'}, status=404)
    
    #　測試
    # 使用 unittest 執行測試
    result_code, success = run_test_cases(code, question_id)
            
    # 只有 AC 或 WA 才能提交
    if result_code not in ['AC', 'WA']:
        return JsonResponse({
            'message': f'程式碼有錯誤 ({result_code})，請修正後再提交'
        }, status=400)
    
    # 檢查是否已經有答案
    answer, created = Answer.objects.get_or_create(user=request.user, question=question)
    answer.answer = code
    answer.save()

    # 建立 Transcript
    Transcript.objects.create(user=request.user, answer=answer, result_code=result_code)
    
    return JsonResponse({
        'message': '答案已成功提交！', 
        'redirect_url': reverse('QuestionDetail', args=[question_id])
    })

def normalize_code_encoding(code):
    """標準化程式碼編碼"""
    if isinstance(code, bytes):
        # 如果是 bytes，嘗試檢測編碼
        try:
            detected = chardet.detect(code)
            if detected['confidence'] > 0.7:
                return code.decode(detected['encoding'], errors='replace')
            else:
                # 嘗試常見編碼
                for encoding in ['utf-8', 'big5', 'gbk', 'gb2312', 'cp950', 'cp936']:
                    try:
                        return code.decode(encoding, errors='replace')
                    except UnicodeDecodeError:
                        continue
                # 最後嘗試 UTF-8
                return code.decode('utf-8', errors='replace')
        except:
            return code.decode('utf-8', errors='replace')
    else:
        # 如果是字串，確保是 UTF-8
        return str(code)

def answer_debug(request):
    """實作debug功能"""
    if request.method != 'POST':
        return JsonResponse({'message': '只允許 POST 請求'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'message': '請先登入'}, status=403)
    
    code = request.POST.get('code', '').strip()
    if not code:
        return JsonResponse({'message': '程式碼不得為空'}, status=400)
    
    question_id = request.POST.get('question_id')
    if not question_id:
        return JsonResponse({'message': '缺少題目編號'}, status=400)
    
    try:
        question = Question.objects.get(id=question_id, is_approved=True)
        if request.user == question.user:
            return JsonResponse({'message': '您不能提交自己的答案', 'redirect_url': reverse('QuestionDetail', args=[question_id])}, status=403)
    except Question.DoesNotExist:
        return JsonResponse({'message': '題目不存在'}, status=404)
    
    # 標準化程式碼編碼
    code = normalize_code_encoding(code)

    # 使用 glottest 執行測試
    result_code, success = run_test_cases(code, question_id)
    
    # 獲取輸入輸出範例用於顯示
    inputs = [line.strip() for line in question.input_example.strip().splitlines() if line.strip()]
    outputs = [line.strip() for line in question.output_example.strip().splitlines() if line.strip()]

    # 建立 Debug
    Debug.objects.create(user=request.user, code=code, result_code=result_code)
    
    return JsonResponse({
        'result_code': result_code,
        'success': success,
        'inputs': inputs,
        'outputs': outputs
    })