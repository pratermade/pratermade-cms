from django.shortcuts import render
from django.views.generic import TemplateView, RedirectView, View, FormView
from django.db.models import Q
from django.urls import reverse
from .models import Article, GlobalContent, Settings as SiteSettings

from .forms import ArticleForm
from django.shortcuts import get_object_or_404, redirect
from braces.views import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import Group, User
import pprint, ss_cms.settings as Settings
import boto3, re
from django.http import JsonResponse, HttpResponse
from PIL import Image
import tempfile
from storages.backends.s3boto3 import S3Boto3Storage
import tempfile
import os
# Create your views here.


class MyTemplateMixin(object):
    #
    # Parent Class Only
    #
    def get_context_data(self, *args, **kwargs):
        context = super(MyTemplateMixin, self).get_context_data(*args, **kwargs)
        context['menu'] = get_menu()
        context['can_edit'] = False
        page_group = None
        if 'slug' in self.kwargs:
            page = get_object_or_404(Article, slug=self.kwargs['slug'])
            page_group = page.group
            context['slug'] = self.kwargs['slug']
            context['breadcrumbs'] = get_breadcrumbs(page.id)
        if page_group is None:
            return context
        if self.request.user.is_superuser or \
                self.request.user == Article.objects.get(slug=self.kwargs['slug']).owner or \
                self.request.user.groups.filter(id=page_group.id).exists() or \
                self.request.user.groups.filter(name='editor').exists():
                    context['can_edit'] = True
                    context['slug'] = self.kwargs['slug']
        global_content = {}
        contents = GlobalContent.objects.all()
        for content in contents:
            global_content[content.name] = content.content
        context['global_content'] = global_content
        context['site_settings'] = SiteSettings.objects.all()[0]
        return context

class MyArticleMixin(MyTemplateMixin):

    def get_context_data(self, *args, **kwargs):
        context = super(MyArticleMixin, self).get_context_data(**kwargs)
        article = get_object_or_404(Article, slug=self.kwargs['slug'])
        gcbs = GlobalContent.objects.all()
        for gcb in gcbs:
            article.content = article.content.replace("{{ " + gcb.name + " }}", gcb.content)
        context['article'] = article
        return context

class IndexView(MyTemplateMixin, TemplateView):
    template_name = "index.html"


class GenericView(MyTemplateMixin, TemplateView):
    template_name = "generic.html"


class ElementsView(MyTemplateMixin, TemplateView):
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


class ArticleView(MyArticleMixin, TemplateView):
    template_name = "generic.html"

class ArticleEditView(UserPassesTestMixin, MyArticleMixin, FormView):
    template_name = "edit_generic.html"
    raise_exeption = True
    form_class = ArticleForm

    def test_func(self, user):
        return has_edit_permission(user, self.kwargs['slug'])
    
    def get_context_data(self, *args, **kwargs):
        return super(ArticleEditView, self).get_context_data(*args, **kwargs)

    def form_invalid(self, form):
        print(form.errors)
        return super(ArticleEditView, self).form_invalid(form)

    def form_valid(self, form):
        article = Article.objects.get(slug=self.kwargs['slug'])
        article.title = form['title'].value()
        article.content = form['content'].value()
        article.page_type = form['page_type'].value()
        article.group_id = form['group'].value()
        article.parent_id = form['parent'].value()
        article.order = form['order'].value()
        article.save()
        return super(ArticleEditView, self).form_valid(form)

    def get_initial(self):
        self.success_url = reverse('page', kwargs={'slug':self.kwargs['slug']})
        article = Article.objects.get(slug=self.kwargs['slug'])
        initial = {
            "page_type": article.page_type,
            "title": article.title,
            "content": article.content,
            "header_image": article.header_image,
            "slug": article.slug,
            "group": article.group,
            "owner": article.owner,
            "link": article.link,
            "parent": article.parent,
            "order": article.order
        }
        return initial
    #     return get_object_or_404(Article, slug=self.kwargs['slug'])


class TocView(MyArticleMixin, TemplateView):
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


class ImageBrowserView(MyTemplateMixin, TemplateView):
    template_name = "image_browser.html"


class FileBrowserView(MyTemplateMixin, TemplateView):
    template_name = "file_browser.html"


class ListImagesView(LoginRequiredMixin, View):

    def get(self, user):
        """
        This is a root request. First find all the views that they have access to and return them as folders.
        """
        groups = self.request.user.groups.all()
        response = '<ul class="jqueryFileTree" style="display: float;">'
        articles = Article.objects.filter(Q(owner=self.request.user) | Q(group__in=groups))
        for article in articles:
            response += '<li class="directory collapsed"><a href="#" rel="{}/">{}</a></li>'.format(article.slug,
                                                                                                   article.slug)
        response += "</ul>"
        print(response)
        return HttpResponse(response)

    def post(self, user):
        """
        This view returns the directory structure for everything under the 'dir' specified in the post request
        :return: HTML for the AJAX request
        """

        if self.request.POST['dir'] == '/':
            """
            This is a root request. First find all the views that they have access to and return them as folders.
            """
            groups = self.request.user.groups.all()
            response = '<ul class="jqueryFileTree" style="display: float;">'
            articles = Article.objects.filter(Q(owner=self.request.user) | Q(group__in=groups))
            for article in articles:
                response += '<li class="directory collapsed"><a href="#" rel="{}/">{}</a></li>'.format(article.slug,article.slug)
            response += "</ul>"
            print(response)
            return HttpResponse(response)
        else:
            """
            This is a folder request. Lest list the contents of this directory
            """
            groups = self.request.user.groups.all()
            response = '<ul class="jqueryFileTree" style="display: float;">'
            articles = Article.objects.filter(Q(owner=self.request.user) | Q(group__in=groups))
            path = self.request.POST['dir'].split('/')
            prefix = "{}/images/original/".format(path[0])
            if path[1] != '':
                for directory in path[1:]:
                    prefix += directory + "/"
            s3 = boto3.resource("s3")
            my_bucket = s3.Bucket(Settings.AWS_MEDIA_BUCKET_NAME)
            for obj in my_bucket.objects.filter(Prefix=prefix):
                # remove prefix from key
                m = re.search(prefix, obj.key)
                filename = obj.key[m.end():]
                original_url = "https://s3.amazonaws.com/{}/{}".format(Settings.AWS_MEDIA_BUCKET_NAME,obj.key)
                thumbnail_url = original_url.replace('original','150')
                response += '<li class="file2 ext_gif2"><a href="#" thumbnail="{}" rel="{}" class="image_thumbnail"><img src="{}">{}</a></li>'.format(thumbnail_url, original_url, thumbnail_url, filename)
            response += "</ul>"
            print(response)
            return HttpResponse(response)


class ListFilesView(LoginRequiredMixin, View):

    def get(self, user):
        """
        This is a root request. First find all the views that they have access to and return them as folders.
        """
        groups = self.request.user.groups.all()
        response = '<ul class="jqueryFileTree" style="display: float;">'
        articles = Article.objects.filter(Q(owner=self.request.user) | Q(group__in=groups))
        for article in articles:
            response += '<li class="directory collapsed"><a href="#" rel="{}/">{}</a></li>'.format(article.slug,
                                                                                                   article.slug)
        response += "</ul>"
        return HttpResponse(response)


    def post(self, user):
        """
        This view returns the directory structure for everything under the 'dir' specified in the post request
        :return: HTML for the AJAX request
        """

        if self.request.POST['dir'] == '/':
            """
            This is a root request. First find all the views that they have access to and return them as folders.
            """
            groups = self.request.user.groups.all()
            response = '<ul class="jqueryFileTree" style="display: float;">'
            articles = Article.objects.filter(Q(owner=self.request.user) | Q(group__in=groups))
            for article in articles:
                response += '<li class="directory collapsed"><a href="#" rel="{}/">{}</a></li>'.format(article.slug,article.slug)
            response += "</ul>"
            return HttpResponse(response)
        else:
            """
            This is a folder request. Lest list the contents of this directory
            """
            groups = self.request.user.groups.all()
            response = '<ul class="jqueryFileTree" style="display: float;">'
            articles = Article.objects.filter(Q(owner=self.request.user) | Q(group__in=groups))
            path = self.request.POST['dir'].split('/')
            prefix = "{}/images/original/".format(path[0])
            if path[1] != '':
                for directory in path[1:]:
                    prefix += directory + "/"
            s3 = boto3.resource("s3")
            my_bucket = s3.Bucket(Settings.AWS_MEDIA_BUCKET_NAME)
            for obj in my_bucket.objects.filter(Prefix=prefix):
                # remove prefix from key
                m = re.search(prefix, obj.key)
                filename = obj.key[m.end():]
                original_url = "https://s3.amazonaws.com/{}/{}".format(Settings.AWS_MEDIA_BUCKET_NAME,obj.key)
                thumbnail_url = original_url.replace('original','150')
                response += '<li class="file2 ext_gif2"><a href="#" thumbnail="{}" rel="{}" class="image_thumbnail"><img src="{}">{}</a></li>'.format(thumbnail_url, original_url, thumbnail_url, filename)
            response += "</ul>"

            return HttpResponse(response)


class ImageUpload(View):

    def test_func(self, user):
        return has_edit_permission(user, self.kwargs['slug'])

    def post(self, *args, **kwargs):

        s3 = boto3.client('s3')
        #
        # Upload original copy
        #

        file = self.request.FILES['file']
        filepath = "{}/images/original/{}".format(self.kwargs['slug'], self.request.FILES['file'].name)
        res = {'location': 'https://{}/{}/images/original/{}'.format(Settings.AWS_S3_MEDIA_DOMAIN, self.kwargs['slug'], self.request.FILES['file'].name)}
        self.resize_upload(1024, file)
        self.resize_upload(768, file)
        self.resize_upload(300, file)
        self.resize_upload(150, file)
        file.seek(0, os.SEEK_SET)
        s3.upload_fileobj(file, Settings.AWS_MEDIA_BUCKET_NAME, filepath, ExtraArgs={"ACL": "public-read"})
        return JsonResponse(res)

    def resize_upload(self, width, image):
        s3 = boto3.client('s3')

        """ Have to use a workaround to get this to work. Otherwise Boto3 closes the file
            add we cannot reopen it.
        """
        # Seek to the beginning of the file.
        image.seek(0, os.SEEK_SET)
        tempdir = tempfile.gettempdir()
        dest = open(tempdir +'/'+image.name, 'w+b')

        for chunk in image.chunks():
            dest.write(chunk)
        im = Image.open(dest)
        resized = Image.open(dest)
        resized_fp = open(tempdir +'/resized_'+image.name, 'w+b')

        if im.width > width:
            ratio = width / im.width
            height = int(im.height * ratio)
            resized = im.resize((width, height))
        resized.save(resized_fp, im.format)
        resized_fp.close()
        filepath = "{}/images/{}/{}".format(self.kwargs['slug'], str(width), image.name)
        s3.upload_file(tempdir +'/resized_'+image.name, Settings.AWS_MEDIA_BUCKET_NAME, filepath, ExtraArgs={"ACL": "public-read"})
        dest.close()
        resized_fp.close()
        if os.path.isfile(tempdir +'/'+image.name):
            os.remove(tempdir +'/'+image.name)
        if os.path.isfile(tempdir +'/resized_'+image.name):
            os.remove(tempdir + '/resized_'+image.name)


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