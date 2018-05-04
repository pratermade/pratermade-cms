from django.shortcuts import render
from django.views.generic import TemplateView, RedirectView, View, FormView
from django.db.models import Q
from django.urls import reverse
from .models import Article, GlobalContent, Settings as SiteSettings

from .forms import ArticleForm, NewArticleForm, SettingsForm, GlobalContentForm
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


# Create your views here




class MyArticleMixin(object):
    #
    # Parent Class Only
    #

    def get_context_data(self, *args, **kwargs):
        context = super(MyArticleMixin, self).get_context_data(*args, **kwargs)
        context['menu'] = get_menu()
        context['can_edit'] = False
        page_group = None
        if 'slug' in self.kwargs:
            article = get_object_or_404(Article, slug=self.kwargs['slug'])
            if Article.objects.filter(parent=article).exists():
                children = Article.objects.filter(parent=article)
            else:
                children = None
            context['children'] = children
            siblings = Article.objects.filter(parent=article.parent)
            context['siblings'] = siblings.order_by('order')
            gcbs = GlobalContent.objects.all()
            if article.content is not None:
                for gcb in gcbs:
                    article.content = article.content.replace("{{ " + gcb.name + " }}", gcb.content)
                context['article'] = article
            page = get_object_or_404(Article, slug=self.kwargs['slug'])
            page_group = page.group
            context['slug'] = self.kwargs['slug']
            context['breadcrumbs'] = get_breadcrumbs(page.id)
            if self.request.user == Article.objects.get(slug=self.kwargs['slug']).owner or \
                self.request.user == Article.objects.get(slug=self.kwargs['slug']).owner or \
                self.request.user.groups.filter(name='editor').exists():
                    context['can_edit'] = True
                    context['slug'] = self.kwargs['slug']
        if page_group is not None:
            if self.request.user.groups.filter(id=page_group.id).exists():
                context['can_edit'] = True



        if self.request.user.is_superuser:
            context['can_edit'] = True
            context['is_admin'] = True

        global_content = {}
        contents = GlobalContent.objects.all()
        for content in contents:
            global_content[content.name] = content.content
        context['global_content'] = global_content
        context['site_settings'] = SiteSettings.objects.all()[0]
        return context


class IndexView(MyArticleMixin, TemplateView):
    template_name = "index.html"


class GlobalContentView(UserPassesTestMixin, MyArticleMixin, FormView):
    template_name = "global_content.html"
    form_class = GlobalContentForm

    def test_func(self, user):
        return user.is_superuser

    def form_valid(self, form):
        self.success_url = reverse('globalcontent')
        if form['id'].value() == '':
            gcb = GlobalContent()
        else:
            gcb = GlobalContent.objects.get(id=form['id'].value())
        gcb.name = form['name'].value()
        gcb.content = form['content'].value()
        gcb.save()
        return super(GlobalContentView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(GlobalContentView, self).get_context_data(*args, **kwargs)
        gcbs = GlobalContent.objects.all()
        context['globals'] = gcbs
        if 'id' in self.kwargs:
            context['id'] = self.kwargs['id']
        return context

    def get_initial(self):
        initial = None
        if 'id' in self.kwargs:
            gcb = get_object_or_404(GlobalContent,id=self.kwargs['id'])
            initial = {
                'name': gcb.name,
                'content': gcb.content,
                'id': gcb.id,
            }
        return initial


class DeleteGlobalContentView(UserPassesTestMixin, RedirectView):
    def test_func(self, user):
        return user.is_superuser

    def get_redirect_url(self, *args, **kwargs):
        gcb = get_object_or_404(GlobalContent, id=self.kwargs['id'])
        gcb.delete()
        # gcb.save()
        self.url = reverse('globalcontent')
        return super(DeleteGlobalContentView, self).get_redirect_url(*args, **kwargs)


class PageView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):

        # If kwargs are empty, assume it is the home_page that we want.
        if 'slug' in self.kwargs:
            article = Article.objects.get(slug=self.kwargs['slug'])

        else:
            article = SiteSettings.objects.all()[0].home_page

        kwargs = {"slug" : article.slug}
        if article.page_type == 'table_of_contents':
            self.url = reverse('toc', kwargs=kwargs)
        if article.page_type == 'article':
            self.url = reverse('article', kwargs=kwargs)
        if article.page_type == 'link':
            self.url = Article.objects.get(slug=kwargs['slug']).link
        if article.page_type == 'index':
            self.url = reverse('home')

        return super(PageView, self).get_redirect_url(*args, **kwargs)


class ArticleView(MyArticleMixin, TemplateView):
    template_name = "generic.html"
    

class ArticleEditView(UserPassesTestMixin, MyArticleMixin, FormView):
    template_name = "edit_generic.html"
    raise_exeption = True
    form_class = ArticleForm

    def test_func(self, user):
        if 'slug' in self.kwargs:
            return has_edit_permission(user, self.kwargs['slug'])
        else:
            return user.is_superuser

    def form_invalid(self, form):
        return super(ArticleEditView, self).form_invalid(form)

    def form_valid(self, form):
        self.success_url = reverse('page', kwargs={'slug': form['slug'].value()})
        if Article.objects.filter(slug=form['slug'].value()).exists():
            article = Article.objects.get(slug=self.kwargs['slug'])
        else:
            article = Article()
        article.title = form['title'].value()
        article.summary = form['summary'].value()
        article.slug = form['slug'].value()
        article.content = form['content'].value()
        article.page_type = form['page_type'].value()
        article.group_id = form['group'].value()
        article.parent_id = form['parent'].value()
        article.order = form['order'].value()
        article.owner_id = form['owner'].value()
        article.header_image = form['header_image'].value()
        article.link = form['link'].value()
        article.save()
        return super(ArticleEditView, self).form_valid(form)

    def get_initial(self):
        initial = None
        if 'slug' in self.kwargs:
            article = Article.objects.get(slug=self.kwargs['slug'])
            initial = {
                "page_type": article.page_type,
                "title": article.title,
                "content": article.content,
                "summary": article.summary,
                "header_image": article.header_image,
                "slug": article.slug,
                "group": article.group,
                "owner": article.owner,
                "link": article.link,
                "parent": article.parent,
                "order": article.order
            }
        return initial


class NewArticleView(UserPassesTestMixin, MyArticleMixin, FormView):
    template_name = "new_article.html"
    raise_exeption = True
    form_class = NewArticleForm

    def test_func(self, user):
        return user.is_superuser


    def form_invalid(self, form):

        return super(NewArticleView, self).form_invalid(form)

    def form_valid(self, form):
        self.success_url = reverse('edit_article', kwargs={'slug': form['slug'].value()})
        article = Article()
        article.title = form['title'].value()
        article.slug = form['slug'].value()
        article.page_type = form['page_type'].value()
        if form['group'].value() != "":
            article.group_id = form['group'].value()
        if form['parent'].value() != "":
            article.parent_id = form['parent'].value()
        article.order = form['order'].value()
        article.owner_id = form['owner'].value()
        article.header_image = form['header_image'].value()
        article.link = form['link'].value()
        print(article)
        article.save()
        return super(NewArticleView, self).form_valid(form)

    def get_initial(self):
        initial = {
            "owner":self.request.user.id,
            "order":0
        }
        return initial


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


class ImageBrowserView(MyArticleMixin, TemplateView):
    template_name = "image_browser.html"


class FileBrowserView(MyArticleMixin, TemplateView):
    template_name = "file_browser.html"


class ListImagesView(LoginRequiredMixin, View):

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
            response = '<ul class="jqueryFileTree">'
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
            response = '<ul class="jqueryFileTree">'
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
                response += '<li class="file2 ext_gif2"><a href="#" rel="{}" class="image_thumbnail"><img src="{}">{}</a></li>'.format(
                    thumbnail_url, original_url, filename)
            response += "</ul>"
            return HttpResponse(response)


class ListFilesView(LoginRequiredMixin, View):

    def get(self, user):
        """
        This is a root request. First find all the views that they have access to and return them as folders.
        """
        groups = self.request.user.groups.all()
        response = '<ul class="jqueryFileTree">'
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
            response = '<ul class="jqueryFileTree">'
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
            response = '<ul class="jqueryFileTree">'
            articles = Article.objects.filter(Q(owner=self.request.user) | Q(group__in=groups))
            path = self.request.POST['dir'].split('/')
            prefix = "{}/files/".format(path[0])
            if path[1] != '':
                for directory in path[1:]:
                    prefix += directory + "/"
            s3 = boto3.resource("s3")
            my_bucket = s3.Bucket(Settings.AWS_MEDIA_BUCKET_NAME)
            for obj in my_bucket.objects.filter(Prefix=prefix):
                # remove prefix from key
                m = re.search(prefix, obj.key)
                filename = obj.key[m.end():]
                extension = filename.split('.')[1]
                print('listing files')
                original_url = "https://s3.amazonaws.com/{}/{}".format(Settings.AWS_MEDIA_BUCKET_NAME,obj.key)
                response += '<li class="file ext_{}"><a href="#" rel="{}">{}</a></li>'.format(extension, original_url,
                                                                                              filename)
            response += "</ul>"

            return HttpResponse(response)


class ListPagesView(LoginRequiredMixin, View):

    def post(self, user):
        """
        This view returns the directory structure for everything under the 'dir' specified in the post request
        :return: HTML for the AJAX request
        """

        if self.request.POST['dir'] == '/':
            """
            This is a root request. First find all the views that they have access to and return them as folders.
            """

            response = '<ul class="jqueryFileTree">'
            articles = Article.objects.filter(parent__isnull=True)

            for article in articles:
                url = "/page/{}".format(article.slug)
                expand = Settings.STATIC_URL + "assets/jquery.fileTree/images/expand.gif"
                response += '''
                                <li class="directory collapsed"><a href="#" rel="{}/">
                                {}</a></li>
                                '''.format(article.slug, article.title)
            response += "</ul>"
            return HttpResponse(response)
        else:
            """
            This is a folder request. Just list the contents of this directory
            """
            slug = self.request.POST['dir']
            slug = slug.replace('/','')
            parent = Article.objects.get(slug=slug)
            response = '''<ul class="jqueryFileTree">
            <li class="file ext_html parent"><a href="#" rel="/page/{}/">{}</a></li>
            '''.format(parent.slug, parent.title)

            articles = Article.objects.filter(parent=parent)
            for article in articles:
                if Article.objects.filter(parent=article):
                    response += '<li class="directory collapsed"><a href="#" rel="{}/">{}</a></li>'.format(article.slug,
                                                                                              article.title)
                else:
                    response += '<li class="file ext_html"><a href="#" rel="/page/{}/">{}</a></li>'.format(article.slug,
                                                                                              article.title)
            response += "</ul>"

            return HttpResponse(response)


class ImageUpload(UserPassesTestMixin, View):

    def test_func(self, user):
        if has_edit_permission(user, self.kwargs['slug']) or user.is_superuser:
            return True
        return False

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


class FileUpload(UserPassesTestMixin, View):

    def test_func(self, user):
        return has_edit_permission(user, self.kwargs['slug'])

    def post(self, *args, **kwargs):

        s3 = boto3.client('s3')
        #
        # Upload original copy
        #

        file = self.request.FILES['file']
        filepath = "{}/files/{}".format(self.kwargs['slug'], self.request.FILES['file'].name)
        res = {"success": True, "error": ""}
        # res = {'location': 'https://{}/{}/files/{}'.format(Settings.AWS_S3_MEDIA_DOMAIN, self.kwargs['slug'], self.request.FILES['file'].name)}
        s3.upload_fileobj(file, Settings.AWS_MEDIA_BUCKET_NAME, filepath, ExtraArgs={"ACL": "public-read"})
        return JsonResponse(res)


class EditSettingsView(UserPassesTestMixin, MyArticleMixin, FormView):
    template_name = "settings.html"
    form_class = SettingsForm

    def test_func(self, user):
        return user.is_superuser

    def form_valid(self, form):
        self.success_url = reverse('index')
        if SiteSettings.objects.all().exists():
            settings = SiteSettings.objects.all()[0]
        else:
            settings = SiteSettings()
        settings.site_name = form['site_name'].value()
        settings.site_tag_line = form['site_tag_line'].value()
        settings.www_root = form['www_root'].value()
        settings.home_page_id = form['home_page'].value()
        settings.theme = form['theme'].value()
        settings.save()
        return super(EditSettingsView, self).form_valid(form)

    def get_initial(self):
        settings = SiteSettings.objects.all()[0]
        initial = {
            'site_name':settings.site_name,
            'site_tag_line': settings.site_tag_line,
            'www_root': settings.www_root,
            'home_page': settings.home_page,
            'theme': settings.theme,
        }
        return initial


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
    print(current)
    print(SiteSettings.objects.all()[0].home_page)
    while current is not None and current != SiteSettings.objects.all()[0].home_page:
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
    id = None
    if article.group is not None:
        id = article.group.id

    if user.groups.filter(id=id).exists() or user == article.owner or user.is_superuser:
        return True
    else:
        return False



