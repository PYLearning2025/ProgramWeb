from django.contrib import admin
from .models import Stage

class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('-created_at',)

admin.site.register(Stage, StageAdmin)