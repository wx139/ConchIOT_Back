# Generated by Django 3.0.3 on 2020-05-09 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0006_auto_20200509_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devices',
            name='addtime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]