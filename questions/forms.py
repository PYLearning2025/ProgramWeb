from django import forms
from django.core.exceptions import ValidationError
from .models import Question, QuestionHistory, QuestionTag, Topic

class QuestionForm(forms.ModelForm):
    def clean_topics(self):
        topics = self.cleaned_data.get('topics')
        if not topics or len(topics) == 0:
            raise ValidationError('請至少選擇一個主題')
        if len(topics) > 3:
            raise ValidationError('最多只能選擇3個主題')
        return topics
        
    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags or len(tags) == 0:
            raise ValidationError('請至少選擇一個標籤')
        if len(tags) > 5:
            raise ValidationError('最多只能選擇5個標籤')
        return tags
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(QuestionForm, self).__init__(*args, **kwargs)
        
        # 添加 Bootstrap CSS 類別
        for field_name, field in self.fields.items():
            if field_name in ['topics', 'tags']:
                if field_name == 'topics':
                    field.widget.attrs.update({'id': 'id_topics'})
                elif field_name == 'tags':
                    field.widget.attrs.update({'id': 'id_tags'})
            elif field_name == 'level':
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.URLInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        instance = super(QuestionForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Question
        fields = [
            'title', 
            'content', 
            'level', 
            'topics', 
            'input_format', 
            'output_format', 
            'input_example', 
            'output_example', 
            'tags',
            'answer', 
            'hint', 
            'reference',
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'input_format': forms.Textarea(attrs={'rows': 5}),
            'output_format': forms.Textarea(attrs={'rows': 5}),
            'input_example': forms.Textarea(attrs={'rows': 5}),
            'output_example': forms.Textarea(attrs={'rows': 5}),
            'answer': forms.Textarea(attrs={'hidden': 'true'}),
            'topics': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
            'hint': forms.TextInput(attrs={'placeholder': '給予提示'}),
            'reference': forms.URLInput(attrs={'placeholder': '相關參考資料連結'}),
        }
        labels = {
            'title': '標題',
            'content': '內容',
            'level': '難度',
            'topics': '主題',
            'input_format': '輸入格式',
            'output_format': '輸出格式',
            'input_example': '輸入範例',
            'output_example': '輸出範例',
            'tags': '標籤',
            'answer': '答案',
            'hint': '提示',
            'reference': '參考資料',
        }

class QuestionHistoryForm(forms.ModelForm):
    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags or len(tags) == 0:
            raise ValidationError('請至少選擇一個標籤')
        if len(tags) > 5:
            raise ValidationError('最多只能選擇5個標籤')
        return tags
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(QuestionHistoryForm, self).__init__(*args, **kwargs)
        
        # 添加 Bootstrap CSS 類別
        for field_name, field in self.fields.items():
            if field_name == 'tags':
                # 對於多選框，不添加 form-control
                continue
            elif field_name == 'level':
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        instance = super(QuestionHistoryForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance
        
    class Meta:
        model = QuestionHistory
        fields = [
            'title', 
            'content', 
            'level', 
            'input_format', 
            'output_format', 
            'input_example', 
            'output_example', 
            'tags', 
            'answer', 
            'hint', 
            'reference',
            'version'
        ]
        
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'input_format': forms.Textarea(attrs={'rows': 3}),
            'output_format': forms.Textarea(attrs={'rows': 3}),
            'input_example': forms.Textarea(attrs={'rows': 3}),
            'output_example': forms.Textarea(attrs={'rows': 3}),
            'answer': forms.Textarea(attrs={'rows': 5}),
            'tags': forms.CheckboxSelectMultiple(),
            'hint': forms.TextInput(attrs={'placeholder': '給予提示'}),
            'reference': forms.TextInput(attrs={'placeholder': '相關參考資料'}),
        }
        labels = {
            'title': '標題',
            'content': '內容',
            'level': '難度',
            'input_format': '輸入格式',
            'output_format': '輸出格式',
            'input_example': '輸入範例',
            'output_example': '輸出範例',
            'tags': '標籤',
            'answer': '答案',
            'hint': '提示',
            'reference': '參考資料',
            'version': '版本'
        }

class QuestionTagForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionTagForm, self).__init__(*args, **kwargs)
        
        # 添加 Bootstrap CSS 類別
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    class Meta:
        model = QuestionTag
        fields = ['tag']
        labels = {
            'tag': '標籤'
        }

class TopicForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        
        # 添加 Bootstrap CSS 類別
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    class Meta:
        model = Topic
        fields = ['name', 'c_name']
        labels = {
            'name': '英文名稱',
            'c_name': '中文名稱'
        }

class QuestionDetailForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ['answer_display', 'as_homework', 'is_approved', 'is_active', 'updated_by', 'view_count', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control', 'disabled': True})
