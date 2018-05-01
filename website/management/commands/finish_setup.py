from django.core.management.base import BaseCommand, CommandError
from django.core import management
import getpass
from django.contrib.auth.models import User
from website.models import Article, Settings

class Command(BaseCommand):

    def handle(self, *args, **options):
        management.call_command('makemigrations')
        management.call_command('migrate')

        username = input("User of the site administrator [admin]: ")
        if username == '':
            username = 'admin'
        password1 = getpass.getpass("Superuser password: ")
        password2 = getpass.getpass("Confirm Password: ")
        while password1 != password2:
            print("Passwords do not match.\n")
            password1 = getpass.getpass("Superuser password: ")
            password2 = getpass.getpass("Confirm Password: ")

        super_user = User.objects.create_superuser(username=username, password=password1, email='')

        article = Article.objects.create(
            title='Home',
            page_type='article',
            summary="The main website page",
            content="Here is where the main website content goes",
            slug='home',
            owner=super_user,
            order=0
        )

        site_name = input("Website Name: [Example]: ")
        if site_name == '':
            site_name = 'Example'
        www_root = input("Website URL [http://localhost.com]: ")
        if www_root == '':
            www_root = 'http://localhost'
        homepage = article
        theme = 'editorial'
        settings = Settings.objects.create(
            site_name=site_name,
            www_root=www_root,
            home_page=homepage,
            theme=theme,
        )

        management.call_command('collectstatic')