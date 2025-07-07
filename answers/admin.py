from django.contrib import admin
from .models import Answer

class AnswerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('user', 'question', 'created_at', 'updated_at')
    search_fields = ('user__username', 'question__title')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

admin.site.register(Answer, AnswerAdmin)