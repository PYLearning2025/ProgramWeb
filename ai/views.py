from google import genai
from google.genai import types
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DifficultyEvaluation, DifficultyEvaluationQuestion
from questions.models import Question
from accounts.models import User
from questions.models import Topic
from questions.models import QuestionTag

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@csrf_exempt
def analyze_question(request):
    if request.method == "POST":
        data = request.POST
        title = data.get('title')
        level = data.get('level')
        content = data.get('content')
        input_format = data.get('input_format')
        output_format = data.get('output_format')
        input_example = data.get('input_example')
        output_example = data.get('output_example')
        answer = data.get('answer')
        hint = data.get('hint')
        topics = data.getlist('topics')
        tags = data.getlist('tags')
        question_id = data.get('question_id')

        try:
            system_instruction = (
                "你是一個用來評估程式設計題目難度的 AI 助理，請根據以下標準分析學生所出的題目，並給出："
                "1.題目難度（簡單／中等／困難），"
                "2.評估依據（簡短說明使用哪些語法或概念)，"
                "3.改進建議（可提供提升題目設計品質的建議，像是題目敘述完整度、方便閱讀程度、輸入/輸出格式表達正確度等等），"
                "4.題目標籤(格式為:#for迴圈、#函式等等）。"
                "難度評估標準如下:"
                "簡單:只需要使用基本的語法或概念，例如變數、條件判斷、迴圈等，若沒有跳出基本概念(如複雜的條件判斷)應判定為簡單。"
                "中等:需要使用較多的語法或概念，例如巢狀迴圈、陣列、字典、函式等。"
                "困難:需要使用複雜的語法或概念，例如遞迴、動態規劃、圖論、狀態轉移等。"
                "不要重複敘述題目內容和對解題方法給出建議，僅需要針對題目難度給出評估與建議。"
                "注意:如果你發現輸入內容是程式碼或是無關的文字而不是題目敘述，不要進行難度評估，僅回覆：「請提供題目敘述內容，才能進行難度分析喔 🙂」。"
                "題目可能以文字冒險、角色扮演、指令模擬等方式表達，不要因為語氣或敘事風格而誤判為非題目敘述，只要有明確任務與邏輯要求，即應視為程式設計題目。"
            )
            
            # 用戶輸入的題目內容
            user_message = (
                f"題目標題：{title}\n"
                f"題目描述：{content}\n"
                f"輸入格式：{input_format}\n"
                f"輸出格式：{output_format}\n"
                f"輸入範例：{input_example}\n"
                f"輸出範例：{output_example}\n"
                f"提示：{hint}\n"
            )
            
            # 創建聊天會話
            chat = client.chats.create(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            
            # 發送用戶訊息並獲取 AI 回應
            response = chat.send_message(user_message)
            difficulty_content = response.text
            
            # 獲取對話歷史，包含所有角色的訊息
            conversation_history = []
            for message in chat.get_history():
                conversation_history.append({
                    'role': message.role,  # 'user' 或 'model'
                    'content': message.parts[0].text
                })
            
            # 組織回應結果，包含三種角色的對話結構
            structured_response = {
                'system': {
                    'role': 'system',
                    'content': system_instruction
                },
                'conversation': conversation_history,
                'assistant_response': {
                    'role': 'assistant', 
                    'content': difficulty_content
                }
            }
            
            # 難度判斷
            difficulty_score = "未知"
            if "困難" in difficulty_content:
                difficulty_score = "困難"
            elif "中等" in difficulty_content:
                difficulty_score = "中等"
            elif "簡單" in difficulty_content:
                difficulty_score = "簡單"

            # 將 AI 分析結果存到資料庫
            difficulty_evaluation = DifficultyEvaluation.objects.create(
                difficulty_score=difficulty_score,
                feedback=difficulty_content
            )

            # 處理題目儲存與關聯
            question = None
            if question_id: # 更新題目資料
                try:
                    question = Question.objects.get(id=question_id)
                    question.title = title
                    question.content = content
                    question.level = level
                    question.input_format = input_format
                    question.output_format = output_format
                    question.input_example = input_example
                    question.output_example = output_example
                    question.answer = answer
                    question.hint = hint or ""
                    question.save()
                except Question.DoesNotExist:
                    question = None
            else:
                # 第一次創建題目
                user_id = data.get('user_id') or request.user.id if hasattr(request, 'user') else None
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        question = Question.objects.create(
                            user=user,
                            title=title,
                            content=content,
                            level=level,
                            input_format=input_format,
                            output_format=output_format,
                            input_example=input_example,
                            output_example=output_example,
                            answer=answer,
                            hint=hint or ""
                        )
                        # MTM 關聯處理
                        if topics:
                            topic_objects = Topic.objects.filter(id__in=topics)
                            question.topics.set(topic_objects)
                        if tags:
                            tag_objects = QuestionTag.objects.filter(id__in=tags)
                            question.tags.set(tag_objects)
                    except Exception as e:
                        return JsonResponse({'error': f'Error creating question: {str(e)}'}, status=500)
            # 建立評估與題目的關聯
            if question:
                DifficultyEvaluationQuestion.objects.get_or_create(
                    evaluation=difficulty_evaluation,
                    question=question
                )   

            return JsonResponse({
                'result': difficulty_content,
                'structured_response': structured_response,
                'question_id': question.id if question else None,
                'difficulty_score': difficulty_score
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': '只接受POST請求'}, status=400)
