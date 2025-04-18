from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Student
from django.core.exceptions import ValidationError
import re

class RegisterForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ['username', 'email', 'name', 'student_id', 'password1', 'password2']

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="學校電子郵件",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    
    name = forms.CharField(
        label="姓名",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    student_id = forms.CharField(
        label="學號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # 首字s，中間為學號9個數字，尾端@stu.nute.edu.tw
        pattern = r'^s\d{9}@stu\.ntue\.edu\.tw$'
        if not re.match(pattern, email):
            raise ValidationError("請輸入有效的學校email格式")

        return email
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')

        # 學號格式：9個數字
        pattern = r'^\d{9}$'
        if not re.match(pattern, student_id):
            raise ValidationError("請輸入有效的學號格式")

        return student_id

class LoginForm(forms.Form):

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    remember_me = forms.BooleanField(
        label="記住我",
        required=False, 
        widget=forms.CheckboxInput()
    )