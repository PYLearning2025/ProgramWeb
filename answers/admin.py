from django.contrib import admin
from .models import Answer, Transcript, Debug

class AnswerAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('user', 'question', 'created_at', 'updated_at')
    search_fields = ('user__username', 'question__title')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

class TranscriptAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    list_display = ('user', 'answer', 'result_code', 'created_at')
    search_fields = ('user__username', 'answer__question__title')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

class DebugAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    list_display = ('user', 'code', 'result_code', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(Answer, AnswerAdmin)
admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(Debug, DebugAdmin)