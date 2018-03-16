from django.contrib import admin
from .models import Article, Settings
# Register your models here.


from django.contrib import admin
admin.site.register(Article)
admin.site.register(Settings)