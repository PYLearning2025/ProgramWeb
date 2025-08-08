from django.db import models

class Stage(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name