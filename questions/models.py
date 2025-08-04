from django.db import models
from accounts.models import User

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_questions', verbose_name="擁有者")
    title = models.CharField(max_length=200, blank=False, null=False, verbose_name="標題")
    content = models.TextField(blank=False, null=False, verbose_name="內容")
    level = models.CharField(max_length=10, choices=[
        ('easy', '簡單'),
        ('medium', '中等'),
        ('hard', '困難'),
    ], blank=False, null=False, verbose_name="難度")
    topics = models.ManyToManyField('Topic', blank=False, verbose_name="主題")
    input_format = models.TextField(blank=False, null=False, verbose_name="輸入格式")
    output_format = models.TextField(blank=False, null=False, verbose_name="輸出格式")
    input_example = models.TextField(blank=False, null=False, verbose_name="輸入範例")
    output_example = models.TextField(blank=False, null=False, verbose_name="輸出範例")
    tags = models.ManyToManyField('QuestionTag', blank=False, verbose_name="標籤")
    answer = models.TextField(blank=False, null=False, verbose_name="答案")
    hint = models.CharField(max_length=500, blank=True, null=True, verbose_name="提示")
    reference = models.URLField(max_length=500, blank=True, null=True, verbose_name="參考資料")
    answer_display = models.BooleanField(default=False, blank=False, null=False, verbose_name="顯示答案")
    as_homework = models.BooleanField(default=False, blank=False, null=False, verbose_name="作為作業")
    is_approved = models.BooleanField(default=False, blank=False, null=False, verbose_name="已批准")
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="啟用")
    view_count = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="瀏覽次數")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_questions', verbose_name="更新者")

    class Meta:
        verbose_name = "問題"
        verbose_name_plural = "問題"

    def __str__(self):
        return self.title

class QuestionHistory(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='history', verbose_name="問題")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="擁有者")
    title = models.CharField(max_length=200, blank=False, null=False, verbose_name="標題")
    content = models.TextField(blank=False, null=False, verbose_name="內容")
    topics = models.ManyToManyField('Topic', blank=False, verbose_name="主題")
    level = models.CharField(max_length=10, choices=[
        ('easy', '簡單'),
        ('medium', '中等'),
        ('hard', '困難'),
    ], blank=False, null=False, verbose_name="難度")
    input_format = models.TextField(blank=False, null=False, verbose_name="輸入格式")
    output_format = models.TextField(blank=False, null=False, verbose_name="輸出格式")
    input_example = models.TextField(blank=False, null=False, verbose_name="輸入範例")
    output_example = models.TextField(blank=False, null=False, verbose_name="輸出範例")
    tags = models.ManyToManyField('QuestionTag', blank=False, verbose_name="標籤")
    answer = models.TextField(blank=False, null=False, verbose_name="答案")
    hint = models.CharField(max_length=500, blank=True, null=True, verbose_name="提示")
    reference = models.CharField(max_length=500, blank=True, null=True, verbose_name="參考資料")
    version = models.PositiveIntegerField(default=1, blank=False, null=False, verbose_name="版本")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "問題歷史"
        verbose_name_plural = "問題歷史"

    def __str__(self):
        return self.title

class QuestionLog(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="問題")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="使用者")
    action = models.CharField(max_length=50, choices=[
        ('created', '創建'),
        ('updated', '更新'),
        ('deleted', '刪除'),
    ], blank=False, null=False, verbose_name="動作")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="時間戳")

    class Meta:
        verbose_name = "問題日誌"
        verbose_name_plural = "問題日誌"

    def __str__(self):
        return f"{self.user.username} {self.action} {self.question.title} at {self.timestamp}"

class QuestionTag(models.Model):
    tag = models.CharField(max_length=50, blank=False, null=False, unique=True, verbose_name="標籤")

    class Meta:
        verbose_name = "問題標籤"
        verbose_name_plural = "問題標籤"

    def __str__(self):
        return self.tag

class Topic(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True, verbose_name="英文名稱")
    c_name = models.CharField(max_length=100, blank=False, null=False, unique=True, verbose_name="中文名稱")

    class Meta:
        verbose_name = "主題"
        verbose_name_plural = "主題"

    def __str__(self):
        return self.c_name