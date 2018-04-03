from django.shortcuts import render
from django.views.generic import TemplateView, RedirectView, View
from django.urls import reverse
from .models import Article, Settings as SiteSettings
from django.shortcuts import get_object_or_404, redirect
from braces.views import UserPassesTestMixin
import pprint, pratermade.settings as Settings
import boto3
from django.http import JsonResponse
from PIL import Image
from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile
import os
# Create your views here.


class MyTemplateView(TemplateView):
    #
    # Parent Class Only
    #
    def get_context_data(self, **kwargs):
        context = super(MyTemplateView, self).get_context_data(**kwargs)
        context['menu'] = get_menu()
        context['is_editor'] = False
        context['can_edit'] = False
        page_group = None
        breadcrumbs = []
        if 'slug' in kwargs:
            page = get_object_or_404(Article, slug=kwargs['slug'])
            page_group = page.group
            context['slug'] = kwargs['slug']
            context['breadcrumbs'] = get_breadcrumbs(page.id)
        if self.request.user.is_superuser or self.request.user.groups.filter(name='editor').exists():
            context['is_editor'] = True
        if page_group is None:
            return context
        if self.request.user.is_superuser or \
                self.request.user == Article.objects.get(slug=kwargs['slug']).owner or \
                self.request.user.groups.filter(id=page_group.id).exists():
                    context['can_edit'] = True
                    context['slug'] = kwargs['slug']
        context['site_settings'] = SiteSettings.objects.all()[0]
        return context

class IndexView(MyTemplateView):
    template_name = "index.html"


class GenericView(MyTemplateView):
    template_name = "generic.html"


class ElementsView(MyTemplateView):
    template_name = "elements.html"


class PageView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        article = get_object_or_404(Article, slug=kwargs['slug'])
        if article.page_type == 'table_of_contents':
            self.url = reverse('toc', kwargs={'slug': kwargs['slug']})
        if article.page_type == 'article':
            self.url = reverse('article', kwargs={'slug':kwargs['slug']})
        if article.page_type == 'link':
            self.url = Article.objects.get(slug=kwargs['slug']).link
        return super(PageView, self).get_redirect_url(*args, **kwargs)


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
        return has_edit_permission(user, self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(ArticleEditView, self).get_context_data(**kwargs)
        get_menu()
        context['article'] = get_object_or_404(Article, slug=self.kwargs['slug'])
        return context


class TocView(MyTemplateView):
    template_name = 'toc.html'

    def get_context_data(self, **kwargs):
        context = super(TocView, self).get_context_data(**kwargs)
        parent = get_object_or_404(Article, slug=kwargs['slug'])
        if Article.objects.filter(parent=parent).exists():
            children = Article.objects.filter(parent=parent)
        else:
            children = None
        context['children'] = children
        context['article'] = parent
        return context


class ImageUpload(View):

    def test_func(self, user):
        return has_edit_permission(user, self.kwargs['slug'])

    def post(self, *args, **kwargs):

        s3 = boto3.client('s3', aws_access_key_id='AKIAIQ4V6DUWUHXJBTCQ', aws_secret_access_key='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')
        #
        # Upload original copy
        #

        file = self.request.FILES['file']
        filepath = "{}/images/original/{}".format(self.kwargs['slug'], self.request.FILES['file'].name)
        res = {'location': 'https://{}/{}/images/original/{}'.format(Settings.AWS_S3_MEDIA_DOMAIN, self.kwargs['slug'], self.request.FILES['file'].name)}
        self.resize_upload(1024, self.request.FILES['file'])
        self.resize_upload(768, self.request.FILES['file'])
        self.resize_upload(300, self.request.FILES['file'])
        self.resize_upload(150, self.request.FILES['file'])
        s3.upload_fileobj(file, Settings.AWS_MEDIA_BUCKET_NAME, filepath, ExtraArgs={"ACL": "public-read"})
        return JsonResponse(res)

    def resize_upload(self, width, image):
        s3 = boto3.client('s3', aws_access_key_id='AKIAIQ4V6DUWUHXJBTCQ',
                          aws_secret_access_key='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')
        fp = open(image.name, 'wb+')

        """ Have to use a workaround to get this to work. Otherwise Boto3 closes the file
            add we cannot reopen it.
        """
        # Seek to the beginning of the file.
        image.seek(0, os.SEEK_SET)
        dest = SpooledTemporaryFile()

        for chunk in image.chunks():
            dest.write(chunk)
        im = Image.open(dest)
        resized_fp = SpooledTemporaryFile()

        if im.width > width:
            ratio = width / im.width
            height = int(im.height * ratio)
            resized = im.resize((width, height))
            resized.save(resized_fp, im.format)
        resized_fp.close()
        filepath = "{}/images/{}/{}".format(self.kwargs['slug'], str(width), self.request.FILES['file'].name)
        s3.upload_fileobj(resized_fp, Settings.AWS_MEDIA_BUCKET_NAME, filepath, ExtraArgs={"ACL": "public-read"})
        dest.close()
        resized_fp.close()


class ImageBrowserView(MyTemplateView):
    template_name = "image_browser.html"


def get_menu():
    menu_items = Article.objects.filter(parent__isnull=True, order__gt=0).order_by('order')
    menu = []
    for i, menu_item in enumerate(menu_items):
        item_info = {}
        item_info['title'] = menu_item.title
        if menu_item.slug is not None: item_info['slug'] = menu_item.slug
        if Article.objects.filter(parent=menu_item, order__gt=0).exists():
            sub_items = Article.objects.filter(parent=menu_item, order__gt=0).order_by('order')
            sub_menu = []
            for sub_item in sub_items:
                sub_item_info = {}
                sub_item_info['title'] = sub_item.title
                if sub_item.slug is not None: sub_item_info['slug'] = sub_item.slug
                sub_menu.append(sub_item_info)
            item_info['sub_menu'] = sub_menu
        menu.append(item_info)
    return menu




def get_breadcrumbs(id):
    breadcrumbs = []
    current = Article.objects.get(id=id)

    while current is not None:
        breadcrumbs.append({'title': current.title, 'slug': current.slug })
        if current.parent is not None:
            current = Article.objects.get(id=current.parent.id)
            if current.parent is not None:
                current = Article.objects.get(title=current).parent
            else:
                slug = ''
        else:
            current = None
    return breadcrumbs[::-1]


def debug_print(info):
    if Settings.DEBUG:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(info)

def has_edit_permission(user, slug):
    article = get_object_or_404(Article, slug=slug)
    if user.groups.filter(id=article.group.id).exists() or user == article.owner or user.is_superuser:
        return True
    else:
        return False