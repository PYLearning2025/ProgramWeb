import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .models import DifficultyEvaluation
from questions.models import Question, QuestionHistory
from questions.forms import QuestionForm

def _payload_from_request(data):
    return {
        "title": data.get('title') or "",
        "content": data.get('content') or "",
        "level": data.get('level') or "",
        "input_format": data.get('input_format') or "",
        "output_format": data.get('output_format') or "",
        "input_example": data.get('input_example') or "",
        "output_example": data.get('output_example') or "",
        "answer": data.get('answer') or "",
        "hint": data.get('hint') or "",
        "reference": data.get('reference') or "",
    }


@login_required
def analyze_question(request):
    if request.method == "POST":
        data = request.POST
        data_form = QuestionForm(data)
        if data_form.is_valid():
            try:
                # 整理 payload
                payload = _payload_from_request(data)
                # 初始化模型
                model = init_chat_model(
                    "gemini-2.5-flash",
                    model_provider="google_genai",
                    temperature=0.1,
                    api_key=os.getenv("GEMINI_API_KEY")
                )

                # 指令
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

                # 建立 ChatPromptTemplate
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", system_instruction),
                    ("human", """題目標題：{title}
                    題目描述：{content}
                    輸入格式：{input_format}
                    輸出格式：{output_format}
                    輸入範例：{input_example}
                    輸出範例：{output_example}
                    提示：{hint}""")
                ])

                # LCEL：把 Prompt | Model | Parser 串成一條
                chain = prompt_template | model | StrOutputParser()

                difficulty_content = chain.invoke(payload)

                difficulty_score = "未知"
                if "困難" in difficulty_content:
                    difficulty_score = "困難"
                elif "中等" in difficulty_content:
                    difficulty_score = "中等"
                elif "簡單" in difficulty_content:
                    difficulty_score = "簡單"

                difficulty_evaluation = DifficultyEvaluation.objects.create(
                    difficulty_score=difficulty_score,
                    feedback=difficulty_content
                )

                return JsonResponse({
                    'result': difficulty_content,
                    'evaluation_id': difficulty_evaluation.id,
                    'difficulty_score': difficulty_score,
                    'question_id': payload.get('question_id')
                })
            except Exception as e:
                print(e)
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': '表單驗證失敗，請檢查您的輸入！'})
    return JsonResponse({'error': '只接受POST請求'}, status=400)
