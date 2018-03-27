# modules
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from .models import Article, Settings

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
        artcle = Article.objects.create(page_type='article',
                                        title='test article',
                                        content='test_content',
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
