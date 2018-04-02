from django.contrib import admin
from .models import Article, Settings, Image
# Register your models here.


from django.contrib import admin
admin.site.register(Article)
admin.site.register(Settings)
admin.site.register(Image)
