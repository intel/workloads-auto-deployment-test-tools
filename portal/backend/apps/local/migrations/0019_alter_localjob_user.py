# Generated by Django 3.2.15 on 2022-09-26 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local', '0018_localsetting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localjob',
            name='user',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
