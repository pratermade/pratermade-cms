# Generated by Django 2.0.3 on 2018-03-13 04:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20180313_0418'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.Category'),
        ),
    ]
