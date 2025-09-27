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

class Transcript(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcripts')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='transcripts')
    result_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Transcript by {self.user.username} to {self.answer.question.title}'

class Debug(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debugs')
    code = models.TextField()
    result_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)