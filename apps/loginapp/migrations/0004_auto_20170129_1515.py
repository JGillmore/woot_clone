# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-29 21:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0003_auto_20170129_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='birth_date',
            field=models.DateField(),
        ),
    ]