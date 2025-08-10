from django.contrib import admin
from .models import Unit, Material, MaterialCategory

class UnitAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'get_materials_count', 'created_at']
    list_editable = ['order']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Unit Information', {
            'fields': ('title', 'description', 'order')
        }),
    )
    
    # 獲得教材數量
    def get_materials_count(self, obj):
        return obj.get_materials_count()
    get_materials_count.short_description = '教材數量'

class MaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'order', 'creator', 'created_at']
    list_filter = ['unit', 'creator', 'created_at']
    list_editable = ['order']
    readonly_fields = ['creator', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'unit__title']
    fieldsets = (
        ('Material Information', {
            'fields': ('unit', 'title', 'content', 'order', 'pdf_file')
        }),
    )
    
    # 新建時自動設定創建者
    def save_model(self, request, obj, form, change):
        if not change: 
            obj.creator = request.user
        super().save_model(request, obj, form, change)

class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

admin.site.register(MaterialCategory, MaterialCategoryAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Material, MaterialAdmin)
