from .models import Report, Category, Attachment, Log
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


class ReportForm(forms.ModelForm):
    """統一的回報表單，包含回報內容和附件上傳"""
    
    # 附件欄位 - 單個圖片上傳
    attachment = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/jpeg,image/jpg,image/png',
            'class': 'form-control',
        }),
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png'],
                message='只允許上傳 JPG、JPEG、PNG 格式的圖片。'
            )
        ],
        help_text='支援 JPG、JPEG、PNG 格式，檔案大小不超過 5MB'
    )
    
    class Meta:
        model = Report
        fields = ['category', 'content']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '請選擇回報分類'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '請詳細描述您的問題或建議...'
            }),
        }
        labels = {
            'category': '回報分類',
            'content': '回報內容',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 設定分類欄位的查詢集（只顯示啟用的分類）
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['category'].empty_label = "請選擇分類"
    
    def clean_attachment(self):
        """驗證單個檔案的上傳"""
        attachment = self.cleaned_data.get('attachment')
        
        if attachment:
            # 檢查檔案大小
            max_size = 5 * 1024 * 1024  # 5MB
            if attachment.size > max_size:
                size_in_mb = attachment.size / (1024 * 1024)
                raise ValidationError(f'檔案大小為 {size_in_mb:.2f}MB，超過 5MB 限制')
        
        return attachment
    
    def save(self, commit=True, user=None):
        """保存回報和附件"""
        report = super().save(commit=False)
        if user:
            report.user = user
        
        if commit:
            report.save()
            
            # 處理單個附件上傳
            attachment_file = self.cleaned_data.get('attachment')
            if attachment_file:
                attachment = Attachment(
                    report=report,
                    file=attachment_file,
                    original_filename=attachment_file.name,
                    file_size=attachment_file.size
                )
                attachment.save()
        
        return report