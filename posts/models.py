from django.db import models
from accounts.models import Student
from datetime import timedelta
from django.utils import timezone

# 題目主表（學生出題，包含解答）
class Question(models.Model):
    difficulty_choices = [
        ('select', '請選擇'),
        ('easy', 'easy'),
        ('medium', 'medium'),
        ('hard', 'hard')
    ]
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="created_questions")
    description = models.TextField(blank=True, null=False)
    input_format = models.TextField(blank=True, null=False)
    output_format = models.TextField(blank=True, null=False)
    input_example = models.TextField(blank=True, null=False)
    output_example = models.TextField(blank=True, null=False)
    answer = models.TextField(blank=True, null=True)
    hint = models.TextField(blank=True, null=False)
    difficulty = models.CharField(max_length=10, choices=difficulty_choices, default='select')
    as_homework = models.BooleanField(default=False, blank=True, null=False)
    answer_display = models.BooleanField(default=False, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class QuestionHistory(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="histories")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=False)
    input_format = models.TextField(blank=True, null=False)
    output_format = models.TextField(blank=True, null=False)
    input_example = models.TextField(blank=True, null=False)
    output_example = models.TextField(blank=True, null=False)
    answer = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="created_question_histories")
    difficulty = models.CharField(max_length=10, choices=Question.difficulty_choices, default='select')
    hint = models.TextField(blank=True, null=False)
    as_homework = models.BooleanField(default=False, blank=True, null=False)
    answer_display = models.BooleanField(default=False, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目標籤表
class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="tags")
    tag = models.CharField(max_length=20)

    def __str__(self):
        return self.tag

# 學生作答表(教師指派題目給學生，學生作答)
class StudentAnswer(models.Model):
    STATUS_CHOICES = [
        ('pending', '未作答'),
        ('submitted', '已提交'),
        ('graded', '已評分')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer = models.TextField(blank=True, null=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    score = models.IntegerField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.student} for '{self.question.title}'"

# 學生互評表
class PeerReview(models.Model):
    reviewer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="peer_reviews_given")
    reviewed_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="peer_reviews_received")
    question_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    complexity_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    practice_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    answer_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    readability_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    question_advice = models.TextField(blank=True, null=False)
    answer_advice = models.TextField(blank=True, null=False)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for '{self.reviewed_question}'"

# 教材表
class TeachingMaterial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目留言板
class QuestionComment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=True, null=False)
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter} for '{self.question.title}'"

# 階段表
class Stage(models.Model):
    STAGE_CHOICES = [
        ('create_questions', '出題階段'),
        ('answer_questions', '作答階段'),
        ('peer_review', '互評階段'),
        ('update_questions', '更新題目階段'),
        ('end', '結束'),
        ('all', '全部')
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="stages")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='create_questions')
    started_at = models.DateTimeField(null=True, blank=True)  # 記錄階段開始時間
    time_limit = models.DurationField(default=timedelta(weeks=1))  # 預設時間限制為1週

    def __str__(self):
        return f'{self.student.name} - {self.get_stage_display()}'

    def get_stage_time_limit(self):
        """根據當前階段設定不同的時間限制"""
        stage_time_limits = {
            'create_questions': timedelta(weeks=1),  # 出題階段 1 週
            'answer_questions': timedelta(weeks=2),   # 作答階段 2 週
            'peer_review': timedelta(weeks=1),         # 互評階段 1 週
            'update_questions': timedelta(weeks=1),    # 更新題目階段 1 週
            'end': timedelta(days=0),                  # 結束階段沒有時間限制
        }
        return stage_time_limits.get(self.stage, timedelta(weeks=1))  # 預設時間為 1 週

    def is_time_expired(self):
        """檢查階段是否超過時間限制"""
        if self.started_at is None:
            return False  # 如果未設定開始時間，表示尚未開始，時間未過期
        return (self.started_at + self.get_stage_time_limit()) <= timezone.now()

    def advance_stage(self):
        """進入下一階段，這個方法會依照你的需求調整"""
        if self.student.is_superuser:  # 如果是 superuser，則不進行時間檢查
            return
        if self.is_time_expired() and self.stage != 'end':
            next_stage = self.get_next_stage()
            self.stage = next_stage
            self.started_at = timezone.now()  # 更新開始時間為當前時間
            self.save()

    def get_next_stage(self):
        """根據當前階段返回下一階段"""
        stage_order = ['create_questions', 'answer_questions', 'peer_review', 'update_questions', 'end']
        current_index = stage_order.index(self.stage)
        if current_index < len(stage_order) - 1:
            return stage_order[current_index + 1]
        return self.stage  # 如果是最後一個階段，返回 'end'

# 功能表
class FunctionStatus(models.Model):
    function = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.function

class GPTQuestion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="gpt_questions")
    question = models.TextField(blank=True, null=False)
    answer = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question