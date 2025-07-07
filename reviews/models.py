from django.db import models
from accounts.models import User
from questions.models import Question

# 學生互評表
class PeerReview(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peer_reviews_given")
    reviewed_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="peer_reviews_received")
    question_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    complexity_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    practice_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    answer_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    readability_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    question_advice = models.TextField(blank=True, null=False)
    answer_advice = models.TextField(blank=True, null=False)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for '{self.reviewed_question}'"