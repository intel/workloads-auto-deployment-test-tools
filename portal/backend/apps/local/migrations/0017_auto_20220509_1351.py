# Generated by Django 3.1.1 on 2022-05-09 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local', '0016_auto_20220506_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localjob',
            name='status',
            field=models.CharField(blank=True, default='IN_QUEUE', max_length=30, null=True),
        ),
    ]
