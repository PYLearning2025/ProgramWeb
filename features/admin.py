from django.contrib import admin
from .models import FeatureToggle

@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_enabled', 'created_at', 'updated_at']
    list_filter = ['is_enabled']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_enabled']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'description')
        }),
        ('狀態設定', {
            'fields': ('is_enabled',)
        }),
        ('時間資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
