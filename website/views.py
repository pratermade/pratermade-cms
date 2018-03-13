from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Article, Category
from django.shortcuts import get_object_or_404
from braces.views import UserPassesTestMixin
import pprint, pratermade.settings as Settings
from django.contrib.auth.models import User


# Create your views here.


class MyTemplateView(TemplateView):
    #
    # Parent Class Only
    #
    def get_context_data(self, **kwargs):
        context = super(MyTemplateView, self).get_context_data(**kwargs)
        context['menu'] = get_menu()
        page_group = None
        breadcrumbs = []
        if 'slug' in kwargs:
            page_group = get_object_or_404(Article, slug=kwargs['slug']).group
            context['breadcrumbs'] = get_breadcrumbs(kwargs['slug'])
        if self.request.user.is_superuser or self.request.user.groups.filter(name='editor').exists():
            context['is_editor'] = True
        if page_group is None:
            return context
        if self.request.user.is_superuser or \
                self.request.user == Article.objects.get(slug=kwargs['slug']).owner or \
                self.request.user.groups.filter(id=page_group.id).exists():
                    context['can_edit'] = True
                    context['slug'] = kwargs['slug']
        debugPrint(context['breadcrumbs'])
        debugPrint(context['menu'])
        return context


class IndexView(MyTemplateView):
    template_name = "index.html"


class GenericView(MyTemplateView):
    template_name = "generic.html"


class ElementsView(MyTemplateView):
    template_name = "elements.html"


class ArticleView(MyTemplateView):
    template_name = "generic.html"

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)
        context['article'] = get_object_or_404(Article, slug=self.kwargs['slug'])
        return context


class ArticleEditView(UserPassesTestMixin, MyTemplateView):
    template_name = "edit_generic.html"
    raise_exeption = True

    def test_func(self, user):
        article = get_object_or_404(Article, slug=self.kwargs['slug'])
        if user.groups.filter(id=article.group.id).exists() or user == article.owner or user.is_superuser:
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(ArticleEditView, self).get_context_data(**kwargs)
        get_menu()
        context['article'] = get_object_or_404(Article, slug=self.kwargs['slug'])
        return context


def get_menu():
    menu_items = Category.objects.filter(parent__isnull=True, order__gt=0).order_by('order')
    menu = []
    for i, menu_item in enumerate(menu_items):
        item_info = {}
        item_info['name'] = menu_item.name
        if menu_item.slug is not None: item_info['slug'] = menu_item.slug
        if Category.objects.filter(parent=menu_item, order__gt=0).exists():
            sub_items = Category.objects.filter(parent=menu_item, order__gt=0).order_by('order')
            sub_menu = []
            for sub_item in sub_items:
                sub_item_info = {}
                sub_item_info['name'] = sub_item.name
                if sub_item.slug is not None: sub_item_info['slug'] = sub_item.slug
                sub_menu.append(sub_item_info)
            item_info['sub_menu'] = sub_menu
        menu.append(item_info)
    return menu

def get_breadcrumbs(slug):
    breadcrumbs = []
    current, slug = Article.objects.get(slug=slug).category.name, Article.objects.get(slug=slug).category.slug

    while current is not None:
        breadcrumbs.append({'name': current, 'slug': slug})
        if Category.objects.get(name=current).parent is not None:
            current = Category.objects.get(name=current).parent.name
            if Category.objects.get(name=current).parent is not None:
                slug = Category.objects.get(name=current).parent.slug
            else:
                slug = '#'
        else:
            current = None
    breadcrumbs.append({'name': 'Home', 'slug': '/'})
    return breadcrumbs[::-1]

def debugPrint(info):
    if Settings.DEBUG:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(info)
