# Generated by Django 2.2.5 on 2019-09-19 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0020_assetwithaccountobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetliabilityobject',
            name='owed',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]