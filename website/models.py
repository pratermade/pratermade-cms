from django.db import models

# Create your models here.


from django.contrib.auth.models import Group, User

class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, blank=True)
    slug = models.CharField(max_length=32, null=True, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=1024)
    content = models.TextField()
    header_image = models.ImageField(null=True, blank=True)
    slug = models.CharField(max_length=32)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE, blank=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.title
