# Generated by Django 2.2.5 on 2019-10-01 00:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_goal_goalamount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='monthlyPayment',
        ),
    ]