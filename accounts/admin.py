from django.contrib import admin
from .models import User, Category

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('last_login', 'created_at')
    fieldsets = (
        (None, {
            'fields': ['username', 'email', 'level', 'category', 'is_active', 'last_login', 'created_at']
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'c_name']
    search_fields = ['name', 'c_name']

admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)