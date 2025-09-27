from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# 題目列表
class Question(models.Model):
    question_content = models.TextField(blank=False, null=False)
    question_img = models.ImageField(blank=True, null=True, upload_to='questions/')
    answer = models.CharField(blank=False, null=False, max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    option_a = models.TextField(blank=False, null=False)
    option_b = models.TextField(blank=False, null=False)
    option_c = models.TextField(blank=False, null=False)
    option_d = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.question_content

# 每個卡片的敘述
class Card(models.Model):
    card_name = models.CharField(blank=False, null=False, max_length=50)
    card_description = models.TextField(blank=False, null=False)
    card_image = models.ImageField(blank=True, null=True, upload_to='cards/')
    card_weight = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], blank=False, null=False)

    def __str__(self):
        return self.card_name

# 學生擁有的卡片
class CardRecord(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record for {self.student} at {self.updated_at} - Card: {self.card.card_name}"
    
# AI回覆用表
# 使用者、相關題目、時間、回覆內容
class AIResponse(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    response_time = models.DateTimeField(auto_now_add=True)
    response_content = models.TextField()

    def __str__(self):
        return f"Response by {self.student.username} to {self.question.question_content} at {self.response_time}"

# 紀錄抽卡的遊戲紀錄
class GameLog(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.student.username} at {self.timestamp} - Card: {self.card.card_name}"

# 紀錄學生答題的紀錄
class QuestionLog(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='game_question_logs')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    select = models.CharField(blank=False, null=False, max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])

    def __str__(self):
        return f"Question log for {self.student.username} at {self.timestamp} - Question: {self.question.question_content}"

# 記錄所有點擊的紀錄
class ChallengeLog(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=[
        ('AIsupport', 'AI引導'),
        ('draw', '抽卡'),
        ('answer', '答題')
    ])

    def __str__(self):
        return f"Challenge from {self.student.username} at {self.timestamp} - Action: {self.action}"