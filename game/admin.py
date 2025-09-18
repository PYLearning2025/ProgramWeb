from django.contrib import admin
from .models import Question, Card, CardRecord, AIResponse, GameLog, QuestionLog, ChallengeLog

# Register your models here.
admin.site.register(Question)
admin.site.register(Card)
admin.site.register(CardRecord)
admin.site.register(AIResponse)
admin.site.register(GameLog)
admin.site.register(QuestionLog)
admin.site.register(ChallengeLog)