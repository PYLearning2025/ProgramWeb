from django.contrib import admin
from .models import Question, QuestionHistory, QuestionLog, QuestionTag, Topic

class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('title', 'level', 'is_approved', 'is_active', 'view_count', 'created_at')
    list_filter = ('level', 'is_approved', 'is_active', 'topics', 'tags')
    search_fields = ('title', 'content')
    filter_horizontal = ('topics', 'tags')
    
    fieldsets = (
        ('Question', {
            'fields': ('user', 'title', 'content', 'level', 'topics', 'tags', 'created_at', 'updated_at'),
            'classes': ('wide',)
        }),
        ('Advanced', {
            'fields': ('input_format', 'output_format', 'input_example', 'output_example', 'answer', 'hint', 'reference', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('answer_display', 'as_homework', 'is_approved', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('updated_by',),
            'classes': ('collapse',)
        }),
    )

class QuestionHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('title', 'level', 'version', 'created_at')
    list_filter = ('level', 'version')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
    
    fieldsets = (
        ('Question History', {
            'fields': ('user', 'title', 'content', 'level', 'input_format', 'output_format', 'input_example', 'output_example', 'tags', 'answer', 'version', 'created_at', 'updated_at'),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': ('hint', 'reference'),
            'classes': ('collapse',)
        }),
    )

class QuestionLogAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)
    list_display = ('question', 'user', 'action', 'timestamp')
    list_filter = ('action', 'user')
    search_fields = ('question__title', 'user__username')
    
    fieldsets = (
        ('Question Log', {
            'fields': ('question', 'user', 'action', 'timestamp'),
            'classes': ('wide',)
        }),
    )

class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    search_fields = ('tag',)
    
    fieldsets = (
        ('Tag', {
            'fields': ('tag',),
            'classes': ('wide',)
        }),
    )

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'c_name')
    search_fields = ('name', 'c_name')
    
    fieldsets = (
        ('Topic', {
            'fields': ('name', 'c_name'),
            'classes': ('wide',)
        }),
    )

admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionHistory, QuestionHistoryAdmin)
admin.site.register(QuestionLog, QuestionLogAdmin)
admin.site.register(QuestionTag, QuestionTagAdmin)
admin.site.register(Topic, TopicAdmin)