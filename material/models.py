from django.db import models
from accounts.models import User

# 單元模型
class Unit(models.Model):
    title = models.CharField(max_length=200, verbose_name="單元標題")
    description = models.TextField(blank=True, verbose_name="單元描述")
    order = models.PositiveIntegerField(verbose_name="排序順序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ['order']
        verbose_name = "單元"
        verbose_name_plural = "單元"

    def __str__(self):
        return self.title

    def get_materials_count(self):
        return self.materials.count()

# 教材模型
class Material(models.Model):
    unit = models.ForeignKey(Unit, related_name='materials', on_delete=models.CASCADE, verbose_name="所屬單元")
    category = models.ForeignKey('MaterialCategory', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="教材類型")
    title = models.CharField(max_length=200, verbose_name="教材標題")
    content = models.TextField(blank=True, verbose_name="教材描述")
    order = models.PositiveIntegerField(verbose_name="排序順序")
    pdf_file = models.FileField(upload_to='materials/pdfs/', verbose_name="PDF檔案")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="建立者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ['order']
        verbose_name = "教材"
        verbose_name_plural = "教材"

    def __str__(self):
        return f"{self.unit.title} - {self.title}"
    
# 教材類型模型
class MaterialCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="類型名稱")
    description = models.TextField(blank=True, verbose_name="類型描述")

    class Meta:
        verbose_name = "教材類型"
        verbose_name_plural = "教材類型"

    def __str__(self):
        return self.name

