from django.contrib import admin
from .models import Report, Category, Attachment, Log

class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('user__username', 'content')

    fieldsets = (
        ('回報資訊', {
            'fields': ('user', 'category', 'content', 'status', 'created_at', 'updated_at'),
            'classes': ('wide',)
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)

    fieldsets = (
        ('分類資訊', {
            'fields': ('name', 'description', 'is_active'),
            'classes': ('wide',)
        }),
    )

class AttachmentAdmin(admin.ModelAdmin):
    readonly_fields = ('original_filename', 'file_size', 'created_at', 'updated_at')
    list_display = ('report', 'file', 'original_filename', 'file_size', 'created_at')
    search_fields = ('report__user__username', 'original_filename')
    list_filter = ('report__status', 'report__category')
    
    fieldsets = (
        ('附件資訊', {
            'fields': ('report', 'file', 'original_filename', 'file_size', 'created_at', 'updated_at'),
            'classes': ('wide',)
        }),
    )

class LogAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    list_display = ('report', 'user', 'action', 'created_at')
    search_fields = ('report__user__username', 'user__username')
    list_filter = ('report__status', 'report__category')
    
    fieldsets = (
        ('操作日誌', {
            'fields': ('report', 'user', 'action', 'created_at'),
            'classes': ('wide',)
        }),
    )

admin.site.register(Report, ReportAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Log, LogAdmin)