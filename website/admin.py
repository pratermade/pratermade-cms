from django.contrib import admin
from .models import Article, Settings, Image, GlobalContent
from django.db.models.functions import Lower
# Register your models here.


class GlobalContentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']

    def get_ordering(self, request):
        return [Lower('name')]  # sort case insensitive



class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title','order','page_type','slug','parent','owner','group',)
    search_fields = ['title','content','slug']

    def get_ordering(self, request):
        return [Lower('parent')]  # sort case insensitive




from django.contrib import admin
admin.site.register(Article, ArticleAdmin)
admin.site.register(Settings)
admin.site.register(Image)
admin.site.register(GlobalContent, GlobalContentAdmin)
