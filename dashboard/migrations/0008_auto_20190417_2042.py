# Generated by Django 2.1.5 on 2019-04-17 20:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0007_auto_20190417_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='User',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='balanceCurrent',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
