# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-06 09:45
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='step',
            managers=[
                ('joinable', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='trip',
            name='is_joinable',
        ),
    ]
