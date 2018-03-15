from django.db import models

# Create your models here.


from django.contrib.auth.models import Group, User

PAGETYPES = (
    ('link', 'Link'),
    ('article', 'Article'),
    ('table_of_contents', 'Table Of Contents')
)

class Article(models.Model):
    page_type = models.CharField(choices=PAGETYPES, max_length=32, default='article')
    title = models.CharField(max_length=1024)
    content = models.TextField(null=True, blank=True)
    header_image = models.ImageField(null=True, blank=True)
    slug = models.CharField(max_length=32, unique=True,
                            help_text="Must be one lowercase word. You must "
                                "populate either slug or link for proper functionality.")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, help_text="Anyone is this group "
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
