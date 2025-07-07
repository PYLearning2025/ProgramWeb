from django.contrib import admin
from .models import PeerReview

class PeerReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed_question', 'question_accuracy_score', 'complexity_score', 'practice_score', 'answer_accuracy_score', 'readability_score', 'reviewed_at')
    list_filter = ('reviewed_at',)

admin.site.register(PeerReview, PeerReviewAdmin)