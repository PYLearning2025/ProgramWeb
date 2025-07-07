from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Category
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
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

class RegisterForm(UserCreationForm):
    name = forms.CharField(
        label='姓名',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='電子郵件',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    company = forms.CharField(
        label='公司',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    job = forms.CharField(
        label='職稱',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'company', 'job', 'email')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['username'].label = '帳號'  # 預設

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        category_id = self.data.get('category')
        company = cleaned_data.get('company')
        job = cleaned_data.get('job')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                is_student = category.id <= 5
                if is_student:
                    if not username:
                        self.add_error('username', '學生身份必須提供學號')
                    elif User.objects.filter(username=username).exists():
                        self.add_error('username', '此學號已被註冊')
                else:
                    if not company:
                        self.add_error('company', '非學生身份必須提供公司')
                    if not job:
                        self.add_error('job', '非學生身份必須提供職稱')
            except Category.DoesNotExist:
                self.add_error(None, '無效的類別選擇')
        return cleaned_data

