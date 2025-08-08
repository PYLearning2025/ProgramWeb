from django.db import models
from django.contrib.auth.models import AbstractUser

# 使用者登入用模型
class User(AbstractUser):
    email = models.EmailField(blank=True, null=False, unique=True)
    level = models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    c_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name