from django.contrib import admin
from .models import UserInfo

class UserInfoAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ['user',]
        }),
        ('Personal Information', {
            'fields': ['name', 'profile_img', 'gender', 'phone', 'birthday', 'address']
        }),
        ('Education', {
            'fields': ['school', 'major', 'student_id']
        }),
        ('Employment', {
            'fields': ['job', 'company']
        }),
        ('Date', {
            'fields': ['created_at', 'updated_at']
        }),
    )

admin.site.register(UserInfo, UserInfoAdmin)