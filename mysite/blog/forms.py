from django import forms
from .models import Comment, Post


# email sharing form
class EmailPostForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'contact-from-text', 'placeholder': 'Your email address'}))
    to = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'contact-from-text', 'placeholder': 'Email address of recipient'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'contact-from-text', 'placeholder': 'Your message'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'contact-from-text', 'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'class': 'contact-from-text', 'placeholder': 'Your email address'}),
            'body': forms.Textarea(attrs={'class': 'contact-from-text', 'placeholder': 'Your message'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'slug', 'body')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'contact-from-text', 'placeholder': 'Title of your post'}),
            'slug': forms.TextInput(attrs={'class': 'contact-from-text', 'placeholder': 'Post slug'}),
            'body': forms.Textarea(attrs={'class': 'contact-from-text', 'placeholder': 'Body of your post'}),
        }


class TagForm(forms.Form):
    tag = forms.CharField(widget=forms.TextInput(attrs={'class': 'contact-from-text', 'placeholder': 'Your tags'}))


class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'class': 'contact-from-text', 'placeholder': 'Search for it'}))
