# Generated by Django 3.1.1 on 2020-10-01 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managebook', '0002_comment_cached_like'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='comment',
            table='comment_table',
        ),
    ]