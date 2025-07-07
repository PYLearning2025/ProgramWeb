from django import forms
from userinfos.models import UserInfo
from accounts.models import User

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '姓名',
            'gender': '性別',
            'phone': '電話',
            'birthday': '生日',
            'address': '地址',
            'school': '學校',
            'major': '科系',
            'student_id': '學號',
            'job': '職業',
            'company': '公司',
        }

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)
        if category is not None:
            if hasattr(category, 'id'):
                category_id = category.id
            else:
                category_id = int(category)
            if category_id <= 5:
                allowed = ['name', 'school', 'major', 'student_id', 'gender', 'phone', 'birthday', 'address']
            elif category_id > 5:
                allowed = ['name', 'job', 'company', 'gender', 'phone', 'birthday', 'address']
            else:
                allowed = list(self.fields.keys())
            for field in list(self.fields.keys()):
                if field not in allowed:
                    self.fields.pop(field)

class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'email': 'Email',
        }

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['profile_img']
        widgets = {
            'profile_img': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_profile_img',
            }),
        }
        labels = {
            'profile_img': '頭像',
        }