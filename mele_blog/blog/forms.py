from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'type': "text",
                                                                        'class': 'form-control'}))

    email = forms.EmailField(widget=forms.EmailInput(attrs={'type': "email",
                                                            'class': 'form-control',
                                                            'aria-describedby': "emailHelp"}))

    to = forms.EmailField(widget=forms.EmailInput(attrs={'type': "email",
                                                         'class': 'form-control',
                                                         'aria-describedby': "emailHelp"}))

    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'type': "text",
                                                                            'class': 'form-control'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    query = forms.CharField()


class GlobalSearchForm(forms.Form):
    global_query = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'type': "text",
                                                                                'class': 'form-control',
                                                                                'placeholder': "Поиск",
                                                                                'aria-label': "Search"}))



