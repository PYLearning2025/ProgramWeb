from django.db import models
from django.core.validators import FileExtensionValidator
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="分類名稱")
    description = models.TextField(blank=True, verbose_name="分類描述")
    is_active = models.BooleanField(default=True, verbose_name="是否啟用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "回報分類"
        verbose_name_plural = "回報分類"

    def __str__(self):
        return self.name

class Report(models.Model):
    STATUS_CHOICES = [
        ("pending", "待處理"),
        ("in_progress", "處理中"),
        ("approved", "已處理"),
        ("rejected", "棄單"),
        ("closed", "已關閉"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="回報用戶")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="回報分類")
    content = models.TextField(verbose_name="回報內容")
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="pending", verbose_name="狀態")
    
    # 時間戳
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="解決時間")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "回報"
        verbose_name_plural = "回報"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.content}"

    @property
    def is_resolved(self):
        return self.status in ['approved', 'rejected', 'closed']

class Attachment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="attachments", verbose_name="回報")
    file = models.FileField(
        upload_to="reports/attachments/",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="附件圖片"
    )
    original_filename = models.CharField(max_length=255, verbose_name="原始檔名")
    file_size = models.PositiveIntegerField(verbose_name="檔案大小(bytes)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上傳時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "回報附件圖片"
        verbose_name_plural = "回報附件圖片"

    def __str__(self):
        return f"{self.report.user.username} - {self.original_filename}"

    def save(self, *args, **kwargs):
        if not self.original_filename and self.file:
            self.original_filename = self.file.name
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

class Log(models.Model):
    ACTION_CHOICES = [
        ("create", "建立"),
        ("update", "更新"),
        ("delete", "刪除"),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="logs", verbose_name="回報")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="操作使用者")
    action = models.CharField(max_length=255, choices=ACTION_CHOICES, verbose_name="操作類型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作時間")

    class Meta:
        verbose_name = "操作日誌"
        verbose_name_plural = "操作日誌"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report.user.username} - {self.action}"