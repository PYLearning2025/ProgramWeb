from django.db import models
from questions.models import Question

# AI 難度評估與回饋模型
class DifficultyEvaluation(models.Model):
    difficulty_score = models.TextField(verbose_name="AI 難度分數")
    feedback = models.TextField(verbose_name="AI 回饋")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question.title} → {self.difficulty_score}"
    
# 回饋對應題目
class DifficultyEvaluationQuestion(models.Model):
    evaluation = models.ForeignKey(DifficultyEvaluation, related_name='evaluated_questions', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='evaluated_difficulties', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.evaluation} - {self.question.title}"
    
    class Meta:
        unique_together = ('evaluation', 'question')
        verbose_name = "難度評估題目關聯"
        verbose_name_plural = "難度評估題目關聯"