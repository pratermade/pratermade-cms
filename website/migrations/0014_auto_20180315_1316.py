# Generated by Django 2.0.3 on 2018-03-15 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_auto_20180315_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='link',
            field=models.URLField(blank=True, help_text="Use to link to external sites. If used, the field 'slug' is ignored.", null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.CharField(blank=True, help_text='Must be one lowercase word. You must populate either slug or link for proper functionality.', max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='stub',
            field=models.BooleanField(default=False, help_text='Select if the Article is a table of contents. TOC is automatically generated for page. The content field is optional.'),
        ),
    ]