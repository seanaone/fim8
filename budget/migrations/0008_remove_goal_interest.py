# Generated by Django 2.2.5 on 2019-10-01 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0007_goal_savingorpayingoff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='interest',
        ),
    ]
