# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-04 11:04
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import planner.validators


class Migration(migrations.Migration):

    replaces = [('planner', '0001_initial'), ('planner', '0002_auto_20171101_1616')]

    initial = True

    dependencies = [
        ('cities_light', '0006_compensate_for_0003_bytestring_bug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PoolingUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driving_license', models.CharField(blank=True, max_length=10, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(10)])),
                ('birth_date', models.DateField(validators=[planner.validators.validate_adult])),
                ('cellphone_number', models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator(message='Please insert a valid cellphone number', regex='^(\\+\\d{2}){0,1}3{1}\\d{9}$')])),
                ('base_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour_origin', models.TimeField()),
                ('hour_destination', models.TimeField()),
                ('max_price', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('order', models.PositiveIntegerField()),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='city_destination', to='cities_light.City')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='city_origin', to='cities_light.City')),
                ('passengers', models.ManyToManyField(to='planner.PoolingUser')),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_origin', models.DateField()),
                ('max_num_passengers', models.PositiveIntegerField(default=4, validators=[django.core.validators.MaxValueValidator(8), django.core.validators.MinValueValidator(1)])),
                ('is_joinable', models.BooleanField(default=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='driver', to='planner.PoolingUser')),
            ],
        ),
        migrations.AddField(
            model_name='step',
            name='trip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip', to='planner.Trip'),
        ),
        migrations.AlterField(
            model_name='step',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
