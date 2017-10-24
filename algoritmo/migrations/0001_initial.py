# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Caracteristicas',
            fields=[
                ('idcaracteristicas', models.AutoField(serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200, null=True, blank=True)),
                ('seudonimo', models.CharField(max_length=10, null=True, blank=True)),
            ],
            options={
                'db_table': 'caracteristicas',
                'managed': False,
                'verbose_name_plural': 'Caracteristicas',
            },
        ),
        migrations.CreateModel(
            name='Combinaciones',
            fields=[
                ('idcombinaciones', models.AutoField(serialize=False, primary_key=True)),
                ('k1', models.FloatField(null=True, blank=True)),
                ('k2', models.FloatField(null=True, blank=True)),
                ('umbral1', models.FloatField(null=True, blank=True)),
                ('umbral2', models.FloatField(null=True, blank=True)),
                ('cohesion', models.FloatField(null=True, blank=True)),
                ('separacion', models.FloatField(null=True, blank=True)),
                ('estado', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'combinaciones',
                'managed': False,
                'verbose_name_plural': 'Combinaciones',
            },
        ),
        migrations.CreateModel(
            name='ComunidadesFinales',
            fields=[
                ('idcomunidades_finales', models.AutoField(serialize=False, primary_key=True)),
                ('comunidad', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'comunidades_finales',
                'managed': False,
                'verbose_name_plural': 'ComunidadesFinales',
            },
        ),
        migrations.CreateModel(
            name='ComunidadesIniciales',
            fields=[
                ('idcomunidades_iniciales', models.AutoField(serialize=False, primary_key=True)),
                ('comunidad', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'comunidades_iniciales',
                'managed': False,
                'verbose_name_plural': 'ComunidadesIniciales',
            },
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('iddata', models.AutoField(serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'db_table': 'data',
                'managed': False,
                'verbose_name_plural': 'Data',
            },
        ),
        migrations.CreateModel(
            name='Individuos',
            fields=[
                ('idindividuos', models.AutoField(serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200, null=True, blank=True)),
                ('seudonimo', models.CharField(max_length=10, null=True, blank=True)),
            ],
            options={
                'db_table': 'individuos',
                'managed': False,
                'verbose_name_plural': 'Individuos',
            },
        ),
        migrations.CreateModel(
            name='IndividuosHasCaracteristicas',
            fields=[
                ('estado', models.IntegerField(null=True, blank=True)),
                ('id_secundario', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'individuos_has_caracteristicas',
                'managed': False,
                'verbose_name_plural': 'IndividuosHasCaracteristicas',
            },
        ),
        migrations.CreateModel(
            name='IndividuosHasComunidades',
            fields=[
                ('id_secundario', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'individuos_has_comunidades',
                'managed': False,
                'verbose_name_plural': 'IndividuosHasComunidades',
            },
        ),
    ]
