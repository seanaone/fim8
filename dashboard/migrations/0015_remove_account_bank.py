# Generated by Django 2.1.5 on 2019-05-24 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_account_accountid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='bank',
        ),
    ]
