from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {'group': "Группы"}

        def clean_subject(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError('Отсутствует какой-либо текст')
            return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.Textarea(attrs={'class': 'form-control'}),
        }

