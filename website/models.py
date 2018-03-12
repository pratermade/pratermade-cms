from django.db import models

# Create your models here.

from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=1024)
    content = models.TextField()
    header_image = models.ImageField()
    slug = models.CharField(max_length=32)

    def __str__(self):
        return self.title