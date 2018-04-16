from django import forms
from .models import PAGETYPES, Article
from django.contrib.auth.models import Group, User



class ArticleForm(forms.Form):
    title = forms.CharField(max_length=1024, widget=forms.TextInput())
    slug = forms.CharField(max_length=32, widget=forms.TextInput(attrs={}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'editable'}), required=False)
    page_type = forms.CharField(widget=forms.Select(attrs={}, choices=PAGETYPES))
    group = forms.ModelChoiceField(queryset=Group.objects.all(), widget=forms.Select(
        attrs={}), required=False)
    parent = forms.ModelChoiceField(queryset=Article.objects.all(), widget=forms.Select(
        attrs={}), required=False)
    order = forms.CharField(widget=forms.TextInput(attrs={}), required=False)
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(
        attrs={}))
    header_image = forms.ImageField(required=False)
    link = forms.URLField(max_length=1024, widget=forms.TextInput(),required=False)

class NewArticleForm(forms.Form):
    title = forms.CharField(max_length=1024, widget=forms.TextInput())
    slug = forms.CharField(max_length=32, widget=forms.TextInput(attrs={}))
    page_type = forms.CharField(widget=forms.Select(attrs={}, choices=PAGETYPES))
    group = forms.ModelChoiceField(queryset=Group.objects.all(), widget=forms.Select(
        attrs={}), required=False)
    parent = forms.ModelChoiceField(queryset=Article.objects.all(), widget=forms.Select(
        attrs={}), required=False)
    order = forms.CharField(widget=forms.TextInput(attrs={}), required=False)
    owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(
        attrs={}))
    header_image = forms.ImageField(required=False)
    link = forms.URLField(max_length=1024, widget=forms.TextInput(), required=False)


class SettingsForm(forms.Form):
    site_name = forms.CharField(max_length=32, widget=forms.TextInput(attrs={}))
    site_tag_line = forms.CharField(max_length=1024, widget=forms.TextInput(attrs={}), required=False)
    www_root = forms.CharField(max_length=1024, widget=forms.TextInput(attrs={}))
    home_page = forms.ModelChoiceField(queryset=Article.objects.filter(parent__isnull=True), widget=forms.Select(
        attrs={}))


class GlobalContentForm(forms.Form):
    name = forms.CharField(max_length=32, widget=forms.TextInput(attrs={}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'editable'}))