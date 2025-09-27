import requests
import dotenv
import os

dotenv.load_dotenv()

def run_test_cases(student_code, question_id):
    url = os.getenv("GLOT_HOST")
    headers = {
        "X-Access-Token": os.getenv("GLOT_ACCESS_TOKEN"),
        "Content-type": "application/json"
    }
    # 將傳入的編碼做 UTF-8 編碼
    if isinstance(student_code, str):
        student_code = student_code.encode('utf-8').decode('utf-8')
    code_content = student_code
    from questions.models import Question
    try:
        question = Question.objects.get(id=question_id, is_approved=True)
        inputs = [line.strip() for line in question.input_example.strip().splitlines() if line.strip()]
        outputs = [line.strip() for line in question.output_example.strip().splitlines() if line.strip()]
    except Question.DoesNotExist:
        return "CE", False
    data = {
        "image": "glot/python:latest",
        "payload": {
            "language": "python",
            "stdin": "\n".join(inputs),
            "files": [
                {
                    "name": "main.py",
                    "content": code_content
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)
    response = response.json()
    if response["stdout"] is None:
        return "WA", False
    elif response["error"] != '':
        return "WA", False
    else:
        output_lines = response["stdout"].strip().splitlines()
        output_lines = [line.strip() for line in output_lines if line.strip()]
        if output_lines == outputs:
            return "AC", True
        else:
            return "WA", False