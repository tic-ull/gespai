# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-05 09:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0004_auto_20161130_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='planformacion',
            name='asistentes',
            field=models.ManyToManyField(through='gestion.AsistenciaFormacion', to='gestion.Becario'),
        ),
    ]
