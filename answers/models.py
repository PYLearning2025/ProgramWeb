from django.db import models
from accounts.models import User
from questions.models import Question

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                name='unique_user_question_answer'
            )
        ]

    def __str__(self):
        return f'Answer by {self.user.username} to {self.question.title}'