from django.core.management.base import BaseCommand, CommandError
from django.core import management
import ss_cms.settings as WebsiteSettings
import configparser


class Command(BaseCommand):
    help = 'Sets the initial data up for a clean install. Writes the initial config file.'

    def handle(self, *args, **kwargs):
        config = configparser.ConfigParser()
        config.add_section('main')
        media_bucket = input('AWS S3 media bucket name: ')
        config.set('main', 'media-bucket', media_bucket)
        static_bucket = input('AWS S3 static bucket name: ')
        config.set('main', 'static-bucket', static_bucket)
        db_type = input('What kind of database? 1. MySQL or 2. sqllite3: ')
        if db_type == '1':
            config.set('main', 'db_type', 'mysql')
            config.add_section('client')
            host = input("Database host: [localhost]: ")
            if host == '':
                host = "localhost"
            config.set('client', 'host', host)
            database = input("Database: [ss_cms]: ")
            if database == '':
                database = 'ss_cms'
            config.set('client', 'database', database)
            db_user = input('Database User: ')
            config.set('client', 'user', db_user)
            db_pass = input('Database Password: ')
            config.set('client', 'password', db_pass)
            config.set('client', 'default-character-set', 'utf8')

        else:
            config.set('main', 'db_type', 'sqllite')

        with open(WebsiteSettings.BASE_DIR + '/settings.cnf', "w") as fp:
            config.write(fp)