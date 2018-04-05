from django import forms
from .models import PAGETYPES, Article
from django.contrib.auth.models import Group, User



class ArticleForm(forms.Form):
    title = forms.CharField(max_length=1024, widget=forms.Textarea(attrs={'class': 'editable'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'editable'}))
    slug = forms.CharField(max_length=32, widget=forms.TextInput(attrs={}))
    page_type = forms.CharField(widget=forms.Select(attrs={}, choices=PAGETYPES))
    group = forms.ModelChoiceField(queryset=Group.objects.all(), widget=forms.Select(
        attrs={}), required=False)
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(
        attrs={}))
    parent = forms.ModelChoiceField(queryset=Article.objects.all(), widget=forms.Select(
        attrs={}), required=False)
    order = forms.CharField(widget=forms.TextInput(attrs={}), required=False)