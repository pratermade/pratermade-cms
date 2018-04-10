# modules
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
<<<<<<< HEAD
from .models import Article, Settings, GlobalContent
from django.core.management import call_command
=======
from .models import Article, Settings, GlobalContent, Image
>>>>>>> b8b3b904d2f40167f57c0a04223a4b6485aff992

# Create your tests here.

class MyTestCase(TestCase):

    def setUp(self):
        group = Group.objects.create(name='editor')
        frank = User.objects.create_user(username='Frank',
                                         password='something',
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
                                        owner=None,
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

class ListImagesTests(MyTestCase):

    #TODO: Find a way to test this better.
    def test_list_returns_result(self):
        c = Client()
        session = c.login(username='Frank', password='something')
        res = c.get('/listimages/')
        self.assertEqual(res.status_code, 200)


class TableOfContentsTests(MyTestCase):

    def test_for_good_response(self):
        c = Client()
        res = c.get('/article/category/')
        self.assertEqual(res.status_code, 200)

    def test_for_global_content_block(self):
        c = Client()
        res = c.get('/article/article/')
        self.assertContains(res,'AcJ4OcHqI4cMxltIMXoYytM7vIa45iKq', count=2)


class ArticleTests(MyTestCase):

    def test_for_good_response(self):
        c = Client()
        res = c.get('/article/article/')
        self.assertEqual(res.status_code, 200)

    def test_for_global_content_block(self):
        c = Client()
        res = c.get('/article/article/')
<<<<<<< HEAD
        self.assertContains(res,'AcJ4OcHqI4cMxltIMXoYytM7vIa45iKq',count=2)
=======
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
>>>>>>> b8b3b904d2f40167f57c0a04223a4b6485aff992
