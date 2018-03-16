# modules
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from .models import Article

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

class IndexTest(MyTestCase):

    def test_for_good_index_response(self):
        c = Client()
        res = c.get('/')
        self.assertEqual(res.status_code, 200)

