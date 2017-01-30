# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-30 18:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wootapp', '0004_auto_20170130_1129'),
    ]

    operations = [
        migrations.RenameField(
            model_name='items',
            old_name='available_units',
            new_name='units',
        ),
        migrations.AlterField(
            model_name='items',
            name='image',
            field=models.ImageField(upload_to='images/items/'),
        ),
    ]