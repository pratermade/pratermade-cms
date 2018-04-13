from django.db import models

# Create your models here.


from django.contrib.auth.models import Group, User

PAGETYPES = (
    ('article', 'Article'),
    ('link', 'Link'),
    ('table_of_contents', 'Table Of Contents'),
    ('index','Index')
)

class Article(models.Model):
    page_type = models.CharField(choices=PAGETYPES, max_length=32, default='article')
    title = models.CharField(max_length=1024)
    content = models.TextField(null=True, blank=True)
    header_image = models.ImageField(null=True, blank=True)
    slug = models.CharField(max_length=32, unique=True,
                            help_text="Must be one lowercase word. You must "
                                "populate either slug or link for proper functionality.")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, help_text="Anyone in this group "
                                                                                                "can edit.")
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE, blank=True, help_text="The owner can edit.")
    link = models.URLField(null=True, blank=True, help_text="Use to link to external sites. If used, the field 'slug' "
                                                            "is ignored.")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                               help_text="Optional. Used for menu or breadcrumb trail. Empty indicates top level.")
    order = models.IntegerField(default=0, help_text="For menu order. It is recommended that you use increments of 10 "
                                                     "as to allow for easy re-ordering of menu items. A value of 0 "
                                                     "indicates that it is not a menu item.")


    def __str__(self):
        return self.title


class GlobalContent(models.Model):
    name = models.CharField(max_length=32)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "GlobalContent"


class Image(models.Model):
    image_name = models.CharField(max_length=32)
    image_location = models.CharField(max_length=1024)
    image_key = models.CharField(max_length=32)

    def __str__(self):
        return self.image_name


class Settings(models.Model):

    site_name = models.CharField(max_length=32, blank=True, null=True)
    site_tag_line = models.CharField(max_length=1024, blank=True, null=True)
    www_root = models.URLField(max_length=1024, help_text="This is the location where your site is located."
                                                          "http://www.example.com")
    home_page = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Settings"

    def __str__(self):
        return "Settings"
