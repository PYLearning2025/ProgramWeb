from django.db import models

class FeatureToggle(models.Model):
    """
    功能開關模型 - 用於控制系統中各個功能的開啟與關閉
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="功能名稱")
    description = models.TextField(blank=True, verbose_name="功能描述")
    is_enabled = models.BooleanField(default=True, verbose_name="是否啟用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "功能開關"
        verbose_name_plural = "功能開關"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({'啟用' if self.is_enabled else '停用'})"
    
    @classmethod
    def is_feature_enabled(cls, feature_name):
        """
        檢查指定功能是否啟用
        """
        try:
            feature = cls.objects.get(name=feature_name)
            return feature.is_enabled
        except cls.DoesNotExist:
            # 如果功能不存在，預設為啟用
            return True
