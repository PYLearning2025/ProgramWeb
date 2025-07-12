from django.contrib import admin
from .models import DifficultyEvaluation

class DifficultyEvaluationAdmin(admin.ModelAdmin):
    list_display = ['question', 'difficulty_score', 'created_at']
    search_fields = ['question']
    readonly_fields = ['created_at']
    fieldsets = (
        ( 'Question Information', {
            'fields': ('question', 'difficulty_score', 'feedback')
        }),
    )

admin.site.register(DifficultyEvaluation, DifficultyEvaluationAdmin)
