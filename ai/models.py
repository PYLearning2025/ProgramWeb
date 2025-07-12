from django.db import models
from questions.models import Question

# AI難度評估與回饋模型
class DifficultyEvaluation(models.Model):
    question = models.ForeignKey(Question, related_name='difficulties', on_delete=models.CASCADE)
    difficulty_score = models.TextField(verbose_name="AI 難度分數")
    feedback = models.TextField(verbose_name="AI 回饋")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question.title} → {self.difficulty_score}"