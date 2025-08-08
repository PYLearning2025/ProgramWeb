from django import forms
from .models import PeerReview

class PeerReviewForm(forms.ModelForm):
    class Meta:
        model = PeerReview
        fields = [
            'question_accuracy_score',
            'complexity_score',
            'practice_score',
            'answer_accuracy_score',
            'readability_score',
            'question_advice',
            'answer_advice',
        ]
        widgets = {
            'question_accuracy_score': forms.Select(attrs={'class': 'form-select'}),
            'complexity_score': forms.Select(attrs={'class': 'form-select'}),
            'practice_score': forms.Select(attrs={'class': 'form-select'}),
            'answer_accuracy_score': forms.Select(attrs={'class': 'form-select'}),
            'readability_score': forms.Select(attrs={'class': 'form-select'}),
            'question_advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'answer_advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        score_fields = [
            'question_accuracy_score',
            'complexity_score',
            'practice_score',
            'answer_accuracy_score',
            'readability_score',
        ]
        for field in score_fields:
            value = cleaned_data.get(field)
            if value is None or value == 0:
                self.add_error(field, '此欄位必須大於0 (Must be greater than 0)')
        if not cleaned_data.get('question_advice', '').strip():
            self.add_error('question_advice', '建議內容不得為空 (Advice cannot be empty)')
        if not cleaned_data.get('answer_advice', '').strip():
            self.add_error('answer_advice', '建議內容不得為空 (Advice cannot be empty)')
        return cleaned_data
