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
from judge.unittest import run_test_cases

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
    wrapped_code = wrap_student_code(code, question_id)
    if wrapped_code is None:
        return JsonResponse({'message': '題目不存在或未獲批准'}, status=404)
    
    # 產生臨時檔案進行測試
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(wrapped_code)
            student_file = temp_file.name
    except Exception as e:
        return JsonResponse({
            'message': f'檔案寫入錯誤: {str(e)}'
        }, status=500)
    
    try:
        # 使用 unittest 執行測試
        result_code, success = run_test_cases(student_file, question_id, timeout_seconds=10)
        
        # 清理臨時檔案
        os.unlink(student_file)
        
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
        
    except Exception as e:
        # 清理臨時檔案
        if os.path.exists(student_file):
            os.unlink(student_file)
        
        return JsonResponse({
            'message': f'程式碼執行錯誤: {str(e)}'
        }, status=500)

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

def wrap_student_code(code, question_id):
    """包裝學生程式碼，處理輸入輸出"""
    from questions.models import Question
    
    try:
        question = Question.objects.get(id=question_id, is_approved=True)
        inputs = [line.strip() for line in question.input_example.strip().splitlines() if line.strip()]
        outputs = [line.strip() for line in question.output_example.strip().splitlines() if line.strip()]
    except Question.DoesNotExist:
        return None
    
    has_input = 'input(' in code
    has_solution = 'def solution(' in code
    
    if has_solution:
        # 如果已經有 solution 函數，直接使用
        return code
    
    if has_input:
        # 如果有 input() 調用，創建一個特殊的包裝
        wrapped_code = f'''def solution(input_data):
    import sys
    from io import StringIO
    
    # 將輸入數據轉換為可迭代的輸入源
    if isinstance(input_data, str):
        input_lines = [input_data.strip()]
    else:
        input_lines = [str(input_data).strip()]
    
    input_iter = iter(input_lines)
    
    # 模擬 input 函數
    def mock_input(prompt=""):
        try:
            return next(input_iter)
        except StopIteration:
            return ""
    
    # 捕獲輸出
    old_stdout = sys.stdout
    old_input = __builtins__['input'] if isinstance(__builtins__, dict) else __builtins__.input
    sys.stdout = StringIO()
    
    try:
        # 替換 input 函數
        if isinstance(__builtins__, dict):
            __builtins__['input'] = mock_input
        else:
            __builtins__.input = mock_input
        
        # 執行學生程式碼
{chr(10).join("        " + line for line in code.split(chr(10)))}
        
        # 獲取輸出
        output = sys.stdout.getvalue()
        return output.strip()
        
    except Exception as e:
        return f"執行錯誤: {{str(e)}}"
    finally:
        # 恢復原始狀態
        sys.stdout = old_stdout
        if isinstance(__builtins__, dict):
            __builtins__['input'] = old_input
        else:
            __builtins__.input = old_input
'''
    else:
        # 如果沒有 input()，直接包裝捕獲輸出
        wrapped_code = f'''def solution(input_data):
    import sys
    from io import StringIO
    
    # 捕獲輸出
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        # 執行學生程式碼
{chr(10).join("        " + line for line in code.split(chr(10)))}
        
        # 獲取輸出
        output = sys.stdout.getvalue()
        return output.strip()
        
    except Exception as e:
        return f"執行錯誤: {{str(e)}}"
    finally:
        # 恢復原始狀態
        sys.stdout = old_stdout
'''
    
    return wrapped_code

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
    
    # 包裝學生程式碼
    wrapped_code = wrap_student_code(code, question_id)
    if wrapped_code is None:
        return JsonResponse({'message': '題目不存在或未獲批准'}, status=404)

    # 產生學生測試資料
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(wrapped_code)
            student_file = temp_file.name
    except Exception as e:
        return JsonResponse({
            'message': f'檔案寫入錯誤: {str(e)}'
        }, status=500)
    
    try:
        # 使用 unittest 執行測試
        result_code, success = run_test_cases(student_file, question_id, timeout_seconds=5)
        
        # 清理臨時檔案
        os.unlink(student_file)
        
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
        
    except Exception as e:
        # 清理臨時檔案
        if os.path.exists(student_file):
            os.unlink(student_file)
        
        return JsonResponse({
            'message': f'程式碼執行錯誤: {str(e)}'
        }, status=500)