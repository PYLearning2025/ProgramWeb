from django.contrib import admin
from .models import DifficultyEvaluation
from .models import DifficultyEvaluationQuestion

class DifficultyEvaluationAdmin(admin.ModelAdmin):
    list_display = ['difficulty_score', 'created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ( 'Question Information', {
            'fields': ('difficulty_score', 'feedback', 'created_at')
        }),
    )

class DifficultyEvaluationQuestionAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'question']
    search_fields = ['evaluation__question__title', 'question__title']
    readonly_fields = ['evaluation', 'question']   
    fieldsets = (
        ('Evaluation Information', {
            'fields': ('evaluation', 'question')
        }),
    )

admin.site.register(DifficultyEvaluation, DifficultyEvaluationAdmin)
admin.site.register(DifficultyEvaluationQuestion, DifficultyEvaluationQuestionAdmin)
