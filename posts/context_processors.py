from .models import GPTQuestion

def chat_history(request):
    """
    將當前使用者的聊天記錄放入所有模板的 context 中
    """
    if request.user.is_authenticated:
        chats = GPTQuestion.objects.filter(student=request.user)
    else:
        chats = []
    return {'chats': chats}
