from django.contrib.auth.models import User


def create_superuser():
    User.objects.create_superuser('admin', 'steve@pratermade.com', 'MCsn4561!')