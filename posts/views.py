from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.db.models import Count, Case, When, IntegerField, Sum, F, Window
from accounts.models import Student
from .models import Question, StudentAnswer, QuestionHistory, PeerReview, TeachingMaterial, FunctionStatus, GPTQuestion, Stage, GPTLog
from .forms import QuestionForm, StudentAnswerForm, QuestionHistoryForm, PeerReviewForm, QuestionCommentForm, GPTQuestionForm
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import DenseRank
from openai import OpenAI
import os

def get_function_status(function_name):
    """取得功能的狀態"""
    status, created = FunctionStatus.objects.get_or_create(function=function_name, defaults={'status': False})
    return status.status

# 開始階段的邏輯
def start_stage_for_user(student, stage_name):
    """設定非 superuser 的使用者使用時間邏輯"""
    # 確保 stage_name 是有效的，這樣可以避免錯誤
    if stage_name not in dict(Stage.STAGE_CHOICES):
        raise ValueError("Invalid stage name")
    # 創建階段並設置開始時間
    stage, created = Stage.objects.get_or_create(student=student, stage=stage_name)
    if created:
        stage.started_at = timezone.now()  # 設置開始時間
        stage.save()

# 獲取使用者當前的階段
def get_user_stage(student):
    """取得非 superuser 的使用者當前階段"""
    if student.is_superuser:
        # 如果是 superuser，則強制設定階段為 'all'
        stage, created = Stage.objects.get_or_create(student=student, stage='all')
        if created:
            stage.started_at = timezone.now()  # 設置開始時間
            stage.save()
        return 'all'
    # 如果不是 superuser，正常處理階段
    stage = Stage.objects.filter(student=student).first()  # 單次查詢獲取第一條記錄
    if stage:
        stage.advance_stage()  # 進入下一階段
        return stage.stage
    else:
        # 如果沒有階段，則創建並返回初始階段
        start_stage_for_user(student, 'create_questions')
        return 'create_questions'

@login_required(login_url='Login')
# 建立題目的頁面
def question_create(request):
    """
    建立題目的頁面
    Returns:
    HttpResponse: 顯示建立題目的表單
    """
    if get_user_stage(student=request.user) == 'create_questions' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_create'):
            return redirect('Close')
        if request.method == 'POST':
            form = QuestionForm(request.POST, user=request.user)
            if form.is_valid():
                if form.cleaned_data.get('difficulty') == 'select':
                    return JsonResponse({'success': False, 'errors': {'難度': ['未選擇難度']}}, status=400)
                try:
                    creator = Student.objects.get(name=request.user.name)
                except Student.DoesNotExist:
                    return JsonResponse({'success': False, 'errors': {'general': ['找不到對應的學生，請確認使用者資料是否完整']}}, status=400)
                question = form.save(commit=False)
                question.creator = creator
                question.save()
                QuestionHistory.objects.create(
                    question=question,
                    title=question.title,
                    description=question.description,
                    answer=question.answer,
                    input_format=question.input_format,
                    output_format=question.output_format,
                    input_example=question.input_example,
                    output_example=question.output_example,
                    hint=question.hint,
                    creator=creator,
                    created_at=question.created_at
                )
                return JsonResponse({'success': True, 'message': '題目已成功建立！'}, status=200)
            else:
                # 返回詳細的欄位錯誤訊息
                errors = {}
                for field, error_list in form.errors.items():
                    field_label = form.fields[field].label
                    errors[field_label] = error_list
                return JsonResponse({'success': False, 'errors': errors}, status=400)

        form = QuestionForm(user=request.user)
        return render(request, 'questions/question_create.html', {'form': form, 'mode': 'edit'})
    else:
        return redirect('Close')

# 顯示題目的頁面
def question_detail(request, pk):
    """
    顯示題目詳細內容的頁面
    Returns:
    HttpResponse: 顯示題目詳細內容的頁面
    """
    if get_function_status('question_detail'):
        return redirect('Close')
    question = get_object_or_404(Question, pk=pk)
    comments = question.comments.all()  # 獲取所有相關評論

    if request.method == 'POST':
        comment_form = QuestionCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.question = question
            new_comment.commenter = request.user
            new_comment.save()
            return redirect('QuestionDetail', pk=question.pk)
    else:
        comment_form = QuestionCommentForm()

    return render(request, 'questions/question_detail.html', {
        'question': question,
        'comments': comments,
        'comment_form': comment_form,
    })

# 更新題目的頁面
def question_update(request, pk):
    """
    更新題目的頁面
    Returns:
    HttpResponse: 顯示更新題目的表單
    """
    if get_user_stage(student=request.user) == 'create_questions' or get_user_stage(student=request.user) == 'update_questions' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_update'):
            return redirect('Close')
        question = get_object_or_404(Question, pk=pk)
        # 在保存更新之前，將原始資料保存到 QuestionHistory 中
        if request.method == 'POST':
            form = QuestionForm(request.POST, instance=question, user=request.user)
            if form.is_valid():
                changed_fields = form.changed_data  # 獲取有更動的欄位
                # 檢查不允許的欄位是否有被更改
                forbidden_fields = ['title', 'editor', 'difficulty']
                illegal_changes = [field for field in changed_fields if field in forbidden_fields]

                if illegal_changes:
                    # 返回一個 JsonResponse 提示使用者不允許更改這些欄位
                    return JsonResponse({
                        'status': 'error',
                        'message': f"以下欄位不允許更動: {', '.join(illegal_changes)}"
                    })
                # 如果允許更動，則先保存歷史紀錄
                if changed_fields:
                    QuestionHistory.objects.create(
                        question=question,
                        title=question.title,
                        description=question.description,
                        answer=question.answer,
                        input_format=question.input_format,
                        output_format=question.output_format,
                        input_example=question.input_example,
                        output_example=question.output_example,
                        hint=question.hint,
                        creator=request.user,
                    )
                    
                    # 保存新的數據到題目
                    form.save()

                return JsonResponse({'status': 'success', 'message': '題目已成功更新！'})
            else:
                # 如果表單無效，返回表單錯誤
                print(form.errors)
                return JsonResponse({
                    'status': 'error',
                    'message': '表單無效，請檢查輸入資料。',
                    'errors': form.errors
                })
        else:
            form = QuestionForm(instance=question, user=request.user)
        return render(request, 'questions/question_update.html', {'form': form})
    else:
        return redirect('Close')

# 刪除題目按鈕的處理
def question_delete(request, pk):
    """
    刪除題目按鈕的處理
    Returns:
    HttpResponse: 刪除題目後重定向到使用者的題目歷史紀錄頁面
    """
    if get_user_stage(student=request.user) == 'create_questions' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_delete'):
            return redirect('Close')

        question = get_object_or_404(Question, pk=pk)
        question.delete()
        return redirect('UserQuestionHistoryList')
    else:
        return redirect('Close')

def question_review(request, question_id):
    """
    顯示該題目的所有評分
    Returns:
    HttpResponse: 顯示該題目的所有評分
    """
    if get_user_stage(student=request.user) == 'peer_review' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_review'):
            return redirect('Close')

        # 驗證題目是否存在
        question = get_object_or_404(Question, pk=question_id)

        # 檢索該題目的所有評分
        peer_reviews = PeerReview.objects.filter(reviewed_question=question)

        # 傳遞資料到模板
        return render(request, 'questions/question_review.html', {
            'question': question,
            'peer_reviews': peer_reviews,
        })
    else:
        return redirect('Close')

# 學生的作業總攬頁面
def question_assignment_list(request):
    """
    顯示學生所有未提交的作業
    Returns:
    HttpResponse: 顯示學生所有未提交的作業
    """
    if get_user_stage(student=request.user) == 'answer_questions' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_assignment_list'):
            return redirect('Close')
        # 篩選出未被學生提交的作答題目
        questions = Question.objects.filter(
            as_homework=True
        ).exclude(
            Exists(
                StudentAnswer.objects.filter(
                    student=request.user,
                    question=OuterRef('pk'),
                    status='submitted'
                )
            )
        )
        return render(request, 'questions/question_assignment_list.html', {'questions': questions})
    else:
        return redirect('Close')

# 顯示並處理作答的頁面
def question_answer(request, pk):
    """
    顯示並處理作答的頁面
    Returns:
    HttpResponse: 顯示並處理作答的頁面
    """
    if get_user_stage(student=request.user) == 'answer_questions' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_answer'):
            return redirect('Close')
        # 獲取題目，但不主動建立 StudentAnswer
        question = get_object_or_404(Question, pk=pk)
        # 嘗試取得現有作答紀錄，但不自動建立
        student_answer = StudentAnswer.objects.filter(student=request.user, question=question).first()
        if request.method == 'POST':
            if not student_answer:
                # 如果還未建立，僅在送出表單時建立
                student_answer = StudentAnswer(student=request.user, question=question)
            # 如果學生已經提交過作答，不允許再次提交
            if student_answer.status == 'submitted':
                return JsonResponse({"error": "您已經提交過此題的作答，無法再次提交。"}, status=400)
            form = StudentAnswerForm(request.POST, instance=student_answer)
            if form.is_valid():
                # 只允許未評分的作答進行提交或修改
                if student_answer.answer == "":
                    return JsonResponse({"error": "作答不可為空。"})
                if student_answer.status != 'graded':
                    student_answer.submitted_at = timezone.now()
                    student_answer.status = 'submitted'
                    form.save()
                    return JsonResponse({"success": "作答提交成功。"})
                else:
                    return JsonResponse({"error": "作答已經評分，無法修改。"})
            else:
                return JsonResponse({"error": "有欄位未填寫或格式錯誤。"})
        # 如果是 GET 請求，展示表單
        form = StudentAnswerForm(instance=student_answer if student_answer else None)
        return render(request, 'questions/question_answer.html', {
            'question': question,
            'form': form,
            'status': student_answer.status if student_answer else 'unattempted',
            'score': student_answer.score if student_answer and hasattr(student_answer, 'score') else None,
        })
    else:
        return redirect('Close')

# 顯示該題目的歷史紀錄
def question_history_list(request, question_id):
    """
    顯示該題目的歷史紀錄
    Returns:
    HttpResponse: 顯示該題目的歷史紀錄
    """
    if get_user_stage(student=request.user) == 'create_questions' or get_user_stage(student=request.user) == 'update_questions' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_history_list'):
            return redirect('Close')
        # 確保該問題存在
        question = get_object_or_404(Question, pk=question_id)
        # 在視圖中，先查詢資料庫中的資料
        history_records = QuestionHistory.objects.filter(question=question).order_by('-created_at')
        # 將查詢的資料傳遞給模板
        return render(request, 'questions/question_history_list.html', {
            'history_records': history_records,
            'form': QuestionHistoryForm()
        })
    else:
        return redirect('Close')

# 顯示使用者建立的所有題目
def user_question_history_list(request):
    """
    顯示使用者建立的所有題目
    Returns:
    HttpResponse: 顯示使用者建立的所有題目
    """
    if get_user_stage(student=request.user) == 'create_questions' or get_user_stage(student=request.user) == 'update_questions' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_history_list'):
            return redirect('Close')
        # 獲取當前使用者建立的所有題目
        user_questions = Question.objects.filter(creator=request.user).prefetch_related('histories')
        return render(request, 'questions/user_question_history_list.html', {
            'user_questions': user_questions,
        })
    else:
        return redirect('Close')

# 顯示所有可評分的問題列表，排除當前使用者創建的問題
def peer_assessment_list(request):
    """
    顯示所有可評分的問題列表，排除當前使用者創建的問題
    Returns:
    HttpResponse: 顯示所有可評分的問題列表
    """
    if get_user_stage(student=request.user) == 'peer_review' or get_user_stage(student=request.user) == 'all':
        if get_function_status('question_peer_assessment_list'):
            return redirect('Close')
        # 確定當前使用者的已評分記錄
        reviewed_questions = PeerReview.objects.filter(reviewer=request.user)
        # 過濾出當前使用者已作答但未創建的問題
        questions_to_review = Question.objects.filter(
            ~Q(creator=request.user),  # 排除自己創建的問題
            Exists(
                StudentAnswer.objects.filter(
                    question=OuterRef('pk'),  # 匹配問題的主鍵
                    student=request.user     # 僅限當前使用者的回答
                )
            )
        )
        # 構建一個查詢集，添加每個問題的評分狀態和時間
        questions_data = []
        for question in questions_to_review:
            # 檢查該問題是否已評分
            review = reviewed_questions.filter(reviewed_question=question).first()
            questions_data.append({
                'question': question,
                'student': question.creator,
                'is_reviewed': review is not None,
                'reviewed_at': review.reviewed_at if review else None
            })
        return render(request, 'questions/question_peer_assessment_list.html', {'questions_data': questions_data})
    else:
        return redirect('Close')

# 顯示評分頁面
def peer_assessment(request, question_id, reviewer_id=None):
    """
    顯示評分頁面
    Returns:
    HttpResponse: 顯示評分頁面
    """
    if get_user_stage(student=request.user) == 'peer_review' or get_user_stage(student=request.user) == 'all':

        if get_function_status('question_peer_assessment'):
            return redirect('Close')
        question = get_object_or_404(Question, pk=question_id)
        # 檢查是否已經存在評分
        if reviewer_id:
            peer_review = PeerReview.objects.filter(reviewer__id=reviewer_id, reviewed_question=question).first()
            reviewer_name = peer_review.reviewer.name
        else:
            peer_review = PeerReview.objects.filter(reviewer=request.user, reviewed_question=question).first()
        if request.method == 'POST':
            # 僅在沒有提交評分的情況下才允許提交
            if peer_review and peer_review.reviewed_at:
                return JsonResponse({"error": "您已經評分過此題目，無法再次修改。"})
            if not peer_review:
                peer_review = PeerReview(reviewer=request.user, reviewed_question=question)
            form = PeerReviewForm(request.POST, instance=peer_review)
            if form.is_valid():
                # 檢查所有分數欄位是否為 0
                score_fields = ['question_accuracy_score', 'complexity_score', 'practice_score', 'answer_accuracy_score', 'readability_score']
                for field in score_fields:
                    if form.cleaned_data.get(field, 0) == 0:
                        # 顯示錯誤訊息
                        error_message = f"{form.fields[field].label} 的分數不可為 0，請重新填寫！"
                        return render(request, 'questions/question_peer_assessment.html', {
                            'question': question,
                            'form': form,
                            'error_message': error_message
                        })
                peer_review = form.save(commit=False)
                peer_review.reviewed_at = timezone.now()
                peer_review.save()
                return JsonResponse({"success": "評分提交成功！\n送出後無法修改，請確認內容無誤。"})
            else:
                return render(request, 'questions/question_peer_assessment.html', {
                    'question': question,
                    'form': form,
                    'error_message': "有欄位未填寫或格式錯誤，請重新檢查！"
                })
        # GET 請求
        form = PeerReviewForm(instance=peer_review)
        form.fields['reviewer_name'].initial = reviewer_name if reviewer_id else request.user.name
        # 如果已經評分，將表單設置為只讀
        if peer_review and peer_review.reviewed_at:
            for field in form.fields:
                form.fields[field].widget.attrs['disabled'] = True
        return render(request, 'questions/question_peer_assessment.html', {
            'question': question,
            'form': form,
            'is_disabled': peer_review and peer_review.reviewed_at
        })
    else:
        return redirect('Close')

# 顯示教師公告頁面
def teacher_dashboard(request):
    """
    顯示教師公告頁面
    Returns:
    HttpResponse: 顯示教師公告頁面
    """
    if get_function_status('question_teacher_dashboard'):
        return redirect('Close')
    teaching_materials = TeachingMaterial.objects.all()
    return render(request, 'questions/teacher_dashboard.html', {'teaching_materials': teaching_materials})

# 學生排行榜
def student_ranking(request):
    """
    學生排行榜
    Returns:
    HttpResponse: 顯示學生排行榜
    """
    if get_function_status('create_questions'):
        return redirect('Close')
    # 獲取當前使用者
    user = request.user
    # 獲取所有學生的出題數量與排名
    students_with_question_count = (
        Student.objects.annotate(
            question_count=Count('created_questions'),
            rank=Window(
                expression=DenseRank(),
                order_by=F('question_count').desc()
            )
        ).order_by('rank')
    )
    # 獲取當前使用者的出題數量與排名
    user_question_count = None
    for student in students_with_question_count:
        if student.id == user.id:
            user_question_count = {
                'question_count': student.question_count,
                'rank': student.rank
            }
            break
    # 獲取所有學生的總分數與排名
    students_with_scores = (
        Student.objects.annotate(
            total_score=Sum(
                Case(
                    When(answers__question__difficulty='hard', then=20),
                    When(answers__question__difficulty='medium', then=10),
                    When(answers__question__difficulty='easy', then=5),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            rank=Window(
                expression=DenseRank(),
                order_by=F('total_score').desc()
            )
        ).order_by('rank')
    )
    # 獲取當前使用者的總分數與排名
    user_total_score = None
    for student in students_with_scores:
        if student.id == user.id:
            user_total_score = {
                'total_score': student.total_score,
                'rank': student.rank
            }
            break
    return render(request, 'questions/ranking.html', {
        'students_with_question_count': students_with_question_count,
        'students_with_scores': students_with_scores,
        'user_question_count': user_question_count,
        'user_total_score': user_total_score,
    })

def user_dashboard(request):
    """
    顯示使用者資訊版面
    Returns:
    HttpResponse: 顯示使用者資訊版面
    """
    if get_function_status('question_user_dashboard'):
        return redirect('Close')
    # 獲取當前使用者
    user = request.user
    student = Student.objects.get(name=user.name)
    # 查找當前使用者創建的所有問題、作答和評分
    user_questions = Question.objects.filter(creator=student)
    user_answers = StudentAnswer.objects.filter(student=student)
    user_reviews = PeerReview.objects.filter(reviewer=student)
    user_questions_amount = user_questions.count() if user_questions else 0
    user_answers_amount = user_answers.count() if user_answers else 0
    # 計算使用者總分數
    user_score = 0
    for answer in user_answers:
        if answer.question.difficulty == 'hard':
            user_score += 20
        elif answer.question.difficulty == 'medium':
            user_score += 10
        elif answer.question.difficulty == 'easy':
            user_score += 5
        else:
            user_score += 0
    # 渲染模板並傳遞必要的上下文變量
    return render(request, 'user_dashboard.html', {
        'student': student,
        'user_questions_amount': user_questions_amount,
        'user_answers_amount': user_answers_amount,
        'user_questions': user_questions,
        'user_answers': user_answers,
        'user_reviews': user_reviews,
        'user_score': user_score
    })

# 關閉功能頁面
def close_view(request):
    return render(request, 'close.html')

# 維護中畫面
def maintenance_view(request):
    return render(request, 'maintenance.html')

# 錯誤頁面
def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

# 處理GPT API
def ask_gpt(message):
    """處理 GPT API
    arguments:
    message (str): 使用者的問題
    Return: str: OpenAI GPT 回覆的答案
    """
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    # 呼叫 OpenAI API
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一個台灣的教學機器人，專門在 Python 程式學習平台協助學生學習，"
                        "請務必遵守以下所有規則並全程使用繁體中文進行敘述，程式碼一律只能用英文撰寫。"

                        "\n\n【語言規則】"
                        "\n1. 不論任何問題，只能回答跟 Python 有關的內容。"
                        "\n2. 若學生詢問非 Python 語言，請回答：「我目前的專業只涵蓋 Python，其他語言可能無法正確協助您。」"

                        "\n\n【平台任務流程】"
                        "\n本平台有四個功能：出題活動、互動解題、同儕互評、反思修正。請依照每個功能的任務要求與限制進行互動。"

                        "\n\n【功能一：出題活動（學生要自己設計題目）】"
                        "\n- 題目需包含以下 8 個欄位：標題、難易度、輸入格式、輸出格式、輸入範例、輸出範例、作答提示、解答。"
                        "\n- 若學生未填寫完整，可提醒其補足欄位，並要求提供已寫內容供你分析與建議。"
                        "\n- **嚴禁提供完整程式碼作為解答**，只能用敘述方式引導學生撰寫邏輯。"
                        "\n- 若學生要求你幫忙出題，僅能給出「設計方向、情境背景與可能的核心概念」，不可一次給出完整八個欄位內容。"
                        "\n- ✅ 每次提供出題方向建議時，請盡量**隨機或循環切換不同類型的題目方向**，避免題目類型重複造成學生出相似內容。你可以從以下常見類型中選擇建議，並優先推薦尚未被使用過的類型：1. 數學與邏輯推理（例：質數判斷、最大公因數、階層運算）2. 資料分類與統計（例：分類數字、平均值與最大值比較）3. 陣列與矩陣操作（例：方陣驗證、旋轉、合併）4. 字串處理（例：計算字母次數、反轉、比對）5. 輸出格式與圖案生成（例：數字金字塔、對齊格式輸出）6. 日常應用情境模擬（例：溫度分析、消費計算、座位分配）7. 條件判斷與分支邏輯（例：分級制度、判斷是否及格）8. 迴圈應用與模擬（例：模擬簡單遊戲流程或重複輸入）9. 資料結構概念模擬（例：堆疊、佇列、字典運用等基礎模仿）請從上述類型中依情境挑選一個方向，並使用清楚範例與情境敘述進行引導，但**絕對不要一次提供完整八項出題內容**，必須讓學生自己設計題目細節。"

                        "\n\n【功能二：互動解題（學生解題）】"
                        "\n- 學生可能會問解法或卡關，**不可提供完整的可執行程式碼**。"
                        "\n- 可以提供：空洞的範例架構（留空讓學生補）、流程敘述、邏輯判斷方式、觀念引導。"
                        "\n- 若學生貼出部分程式碼並詢問空白處，**只能回應這裡可能需要什麼邏輯或語法，不能直接補齊。**"

                        "\n\n【功能三：同儕互評（學生評分他人題目與解答）】"
                        "\n- 評量向度包含五項：題目正確性、題目複雜性、題目實用性、程式正確性、程式可讀性。"
                        "\n- 評分採 1～4 分制，請依據 rubrics 給出具體的敘述性建議。"
                        "\n- 評語中**不得包含任何程式碼內容**，僅能使用文字評論（如：可以增加說明範例、命名更清楚等等）。"

                        "\n\n【功能四：反思修正（學生修改原題與解答）】"
                        "\n- 學生會根據同儕意見進行修正。你可以協助確認建議是否已被採納。"
                        "\n- 若提供空洞的程式碼，**不能幫學生補齊空白處，只能敘述該處應處理什麼樣的邏輯問題。**"
                        "\n- 可以引導學生撰寫反思，例如：「你這次修改學到了什麼？覺得哪裡還可以再調整？」"

                        "\n\n【安全與反作弊原則】"
                        "\n- 即使學生強烈要求、說急用、表示卡關很久，也**不得提供完整程式碼。**"
                        "\n- 若學生用提示方式引誘提供完整程式，請直接婉拒並鼓勵其理解邏輯。"
                        "\n- 回覆時請多使用問題引導、步驟拆解與思路說明，幫助學生真正學習而不是複製貼上。"

                        "\n\n請你從頭到尾扮演這樣的角色，若有任何違反原則的需求，請堅守以上規則，並以溫和引導語氣提醒對方這是為了幫助他真正學會 Python。"
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=1000,
            temperature=0.2
        )
        ai_reply = completion.choices[0].message.content
    except Exception as e:
        ai_reply = f"發生錯誤：{e}"
    return ai_reply

def chat_view(request):
    """
    顯示聊天頁面
    Returns:
    HttpResponse: 顯示聊天頁面
    """
    if request.method == 'POST':
        form = GPTQuestionForm(request.POST)
        if form.is_valid():
            user_question = form.cleaned_data.get('question')
            ai_reply = ask_gpt(user_question)

            # 去除 HTML 標籤
            user_question = strip_tags(user_question)
            ai_reply = strip_tags(ai_reply)

            if ai_reply.startswith("發生錯誤："):
                new_chat = GPTQuestion(
                    student=request.user,
                    question=user_question,
                    answer="系統錯誤請聯絡系統管理員",
                    created_at=timezone.now()
                )
                new_chat.save()
                gpt_log = GPTLog(
                    student=request.user,
                    question=new_chat,
                    log=ai_reply
                )
                gpt_log.save()
                return JsonResponse({'success': True, 'message': user_question, 'response': "系統錯誤請聯絡系統管理員"})
            else:
                new_chat = GPTQuestion(
                    student=request.user,
                    question=user_question,
                    answer=ai_reply,
                    created_at=timezone.now()
                )
                new_chat.save()
                return JsonResponse({'success': True, 'message': user_question, 'response': ai_reply})
        else:
            print(form.errors)
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    chats = GPTQuestion.objects.filter(student=request.user)
    return render(request, 'sidebars/chat.html', {'chats': chats})