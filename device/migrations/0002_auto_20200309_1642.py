# Generated by Django 3.0.3 on 2020-03-09 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='devices',
            old_name='lng',
            new_name='lng1',
        ),
    ]
