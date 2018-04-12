# modules
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.core.management import call_command
from .models import Article, Settings, GlobalContent, Image
from .forms import ArticleForm
from ss_cms.settings import AWS_MEDIA_BUCKET_NAME, STATIC_URL


# Create your tests here.

class MyTestCase(TestCase):

    def setUp(self):
        group = Group.objects.create(name='editor')
        frank = User.objects.create_user(username='Frank',
                                         password='sometchhing',
                                         first_name='Frank',
                                         last_name='Person')
        ned = User.objects.create_user(username='Ned',
                                       password='somethingelse',
                                       first_name='Ned',
                                       last_name='Spillman')
        ned.groups.add(group)
        category = Article.objects.create(page_type='table_of_contents',
                                          title='test article',
                                          content='test_content',
                                          header_image=None,
                                          slug='category',
                                          group=group,
                                          owner=None,
                                          link='',
                                          parent=None,
                                          order=1)
        article = Article.objects.create(page_type='article',
                                        title='test article',
                                        content='''test_content <h1>{{ global_content_1 }}</h1> here is some more text
                                         {{ global_content_2 }} more test content {{ global_content_1 }} the end of the
                                         test text.''',
                                        header_image=None,
                                        slug='article',
                                        group=group,
                                        owner=ned,
                                        link='',
                                        parent=category,
                                        order=1)
        link = Article.objects.create(page_type='link',
                                      title='test article',
                                      content='test_content',
                                      header_image=None,
                                      slug='link',
                                      group=group,
                                      owner=None,
                                      link='http://www.cnn.com',
                                      parent=category,
                                      order=1)
        settings = Settings.objects.create(site_name='Pratermade', site_tag_line="Tagline here",
                                          www_root="http://127.0.0.1:8900")

        GlobalContent.objects.create(name="global_content_1",content="AcJ4OcHqI4cMxltIMXoYytM7vIa45iKq")
        GlobalContent.objects.create(name="global_content_2", content="ml0o8I8ELlxQZNAjtptoFlzks1Q47HUA")


class IndexTest(MyTestCase):

    def test_for_good_index_response(self):
        c = Client()
        res = c.get('/')
        self.assertEqual(res.status_code, 200)


class MenuCreationTest(MyTestCase):

    def test_for_proper_menu_creation(self):
        c = Client()
        res = c.get('/article/article/')
        menu = [{'title': 'test article', 'slug': 'category', 'sub_menu':
            [{'title': 'test article', 'slug': 'article'}, {'title': 'test article', 'slug': 'link'}]}]
        self.assertEqual(menu,res.context['menu'])


class BreadCrumbCreationTest(MyTestCase):

    def test_for_proper_breadcrumb_creation(self):
        c = Client()
        res = c.get('/article/article/')
        breadcrumbs = [{'title': 'test article', 'slug': 'category'}, {'title': 'test article', 'slug': 'article'}]
        self.assertEqual(breadcrumbs,res.context['breadcrumbs'])


class PermissionsTests(MyTestCase):

    def test_user_cannot_edit(self):
        c = Client()
        session = c.login(username='Frank',password='something')
        res = c.get('/editArticle/article/')
        self.assertEqual(res.status_code, 302)

    def test_user_can_edit(self):
        c = Client()
        session = c.login(username='Ned', password='somethingelse')
        res = c.get('/editArticle/article/')
        self.assertEqual(res.status_code, 200)

    def test_non_editor_in_context(self):
        c = Client()
        session = c.login(username='Frank', password='something')
        res = c.get('/article/article/')
        self.assertFalse(res.context['can_edit'])

    def test_editor_in_context(self):
        c = Client()
        session = c.login(username='Ned', password='somethingelse')
        res = c.get('/article/article/')
        self.assertTrue(res.context['can_edit'])


class TableOfContentsTests(MyTestCase):

    def test_for_good_response(self):
        c = Client()
        res = c.get('/toc/category/')
        self.assertEqual(res.status_code, 200)

    def test_for_global_content_block(self):
        c = Client()
        res = c.get('/toc/category/')
        self.assertTrue('global_content_1' in res.context['global_content'])

    def test_for_children(self):
        c = Client()
        res = c.get('/toc/category/')
        article = Article.objects.get(slug="article")
        self.assertTrue(article in res.context['children'])

    def test_for_no_children(self):
        c = Client()
        res = c.get('/toc/article/')
        article = Article.objects.get(slug="article")
        self.assertTrue(res.context['children'] is None)


class ArticleTests(MyTestCase):

    def test_for_good_response(self):
        c = Client()
        res = c.get('/article/article/')
        self.assertEqual(res.status_code, 200)

    def test_for_global_content_block(self):
        c = Client()
        res = c.get('/article/article/')
        self.assertContains(res,'AcJ4OcHqI4cMxltIMXoYytM7vIa45iKq', count=2)


class ModelTests(MyTestCase):

    def test_global_content_str(self):
        gc = GlobalContent.objects.create(name="test_content_4", content="NBgL78AQbobCHAZnyYwt0xZbPuBMaxlc")
        self.assertTrue(isinstance(gc, GlobalContent))
        self.assertEqual(gc.__str__(), 'test_content_4')

    def test_image_str(self):
        image = Image.objects.create(image_name="test_image", image_location="/somewhere/",
                                     image_key="tiwo24et3t0Q1qJUc4CiPxSqmpgNg5Yc")
        self.assertTrue(isinstance(image, Image))
        self.assertEqual(image.__str__(), 'test_image')

    def test_settings_str(self):
        settings = Settings.objects.all()[0]
        self.assertTrue(isinstance(settings, Settings))
        self.assertEqual(settings.__str__(), 'Settings')

class PageRedirectTest(MyTestCase):

    def test_proper_redirect(self):
        c = Client()
        res = c.get('/page/article/')
        self.assertEqual(res.url, "/article/article/")


class ArticleEditTests(MyTestCase):

    def test_article_edit_view(self):
        c = Client()
        c.login(username='Ned', password='somethingelse')
        res = c.get('/editArticle/article/')
        self.assertEqual(res.status_code, 200)

    def test_good_form_data(self):
        group = Group.objects.get(name="editor")
        article = Article.objects.get(slug="Article")
        data = {
            "title":"Test Title",
            "content": "This is some test content",
            "page_type": "article",
            "group": group.id,
            "parent": article.id,
            "order": "2",
            }
        form = ArticleForm(data=data)
        self.assertTrue(form.is_valid())

    def test_view_with_good_data(self):
        c = Client()
        c.login(username='Ned', password='somethingelse')
        group = Group.objects.get(name="editor")
        article = Article.objects.get(slug="Article")
        data = {
            "title":"Test Title",
            "content": "This is some test content",
            "page_type": "article",
            "group": group.id,
            "parent": article.id,
            "order": "2",
            }
        res = c.post('/editArticle/article/', data)
        self.assertEqual(res.url, "/page/article/")

    def test_view_with_bad_data(self):
        c = Client()
        c.login(username='Ned', password='somethingelse')
        group = Group.objects.get(name="editor")
        article = Article.objects.get(slug="Article")
        data = {
            "title": "",
            "content": "This is some test content",
            "page_type": "article",
            "group": group.id,
            "parent": article.id,
            "order": "2",
        }
        res = c.post('/editArticle/article/', data)
        self.assertFormError(res, 'form', 'title', 'This field is required.')

class ListImageTests(MyTestCase):

    def test_get_imagelist(self):
        c = Client()
        c.login(username='Ned', password='somethingelse')
        res = c.get('/listimages/')
        self.assertEqual(res.status_code, 200)

class ImageUploadTest(MyTestCase):

    def test_image_upload(self):
        c = Client()
        c.login(username='Ned', password='somethingelse')
        fp = open("SSCMS-Logo.png", "rb")
        data = {
            'slug': 'article',
            'file': fp
                }
        res = c.post('/imageupload/article/',data)
        fp.close()
        expected = '{"location": "https://s3.amazonaws.com/'+ AWS_MEDIA_BUCKET_NAME+'/article/images/original/SSCMS-Logo.png"}'
        self.assertEqual(res.content, expected.encode())


class FileUploadTest(MyTestCase):

    def test_image_upload(self):
        c = Client()
        c.login(username='Ned', password='somethingelse')
        fp = open("README.md", "rb")
        data = {
            'slug': 'article',
            'file': fp
                }
        res = c.post('/fileupload/article/',data)
        fp.close()
        expected = '{"success": true, "error": ""}'
        self.assertEqual(res.content, expected.encode())

class ListPagesTest(MyTestCase):

    def test_post_root(self):
        c = Client()
        c.login(username='Ned', password='somethingelse')
        data = {}
        data['dir'] = '/'
        res = c.post('/listpages/', data)
        expected = '<ul class="jqueryFileTree">'
        expected += '''
                                <li class="directory collapsed"><a href="#" rel="category/">
                                test article</a></li>
                                '''
        expected += "</ul>"
        self.assertEqual(res.content, expected.encode())