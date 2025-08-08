from django.db import models

class UserInfo(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='user_info')
    name = models.CharField(max_length=100, blank=True, null=False)
    profile_img = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    school = models.CharField(max_length=100, blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    job = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name if self.name else 'No Name'}"