# Generated by Django 2.2.5 on 2019-10-01 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0008_remove_goal_interest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='savingOrPayingoff',
        ),
        migrations.AddField(
            model_name='goal',
            name='interest',
            field=models.DecimalField(decimal_places=2, default=False, max_digits=15),
            preserve_default=False,
        ),
    ]
