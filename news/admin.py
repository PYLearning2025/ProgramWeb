from django.contrib import admin
from news.models import NewsUnit, NewsCategory, NewsTag

class NewsUnitAdmin(admin.ModelAdmin):
    readonly_fields = ('published_date', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'content', 'image', 'author', 'source_name', 'source_url', 'is_published']
        }),
        ('Tags and Category', {
            'fields': ['tags', 'category']
        }),
        ('Statistics', {
            'fields': ['views_count']
        }),
        ('Date', {
            'fields': ['published_date', 'created_at', 'updated_at']
        }),
    )

class NewsCategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['name', 'c_name']
        }),
    )

class NewsTagAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ['name', 'c_name']
        }),
    )

admin.site.register(NewsUnit, NewsUnitAdmin)
admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(NewsTag, NewsTagAdmin)