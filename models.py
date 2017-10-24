# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Combinaciones(models.Model):
    idcombinaciones = models.AutoField(primary_key=True)
    k1 = models.FloatField(blank=True, null=True)
    k2 = models.FloatField(blank=True, null=True)
    umbral1 = models.FloatField(blank=True, null=True)
    umbral2 = models.FloatField(blank=True, null=True)
    cohesion = models.FloatField(blank=True, null=True)
    separacion = models.FloatField(blank=True, null=True)
    numero_comunidades_finales = models.IntegerField(blank=True, null=True)
    data_iddata = models.ForeignKey('Data', db_column='data_iddata', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'combinaciones'


class ComunidadesFinales(models.Model):
    idcomunidades_finales = models.AutoField(primary_key=True)
    comunidad = models.TextField(blank=True, null=True)
    combinaciones_idcombinaciones = models.ForeignKey(Combinaciones, db_column='combinaciones_idcombinaciones', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comunidades_finales'


class Data(models.Model):
    iddata = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    comunidades_iniciales = models.IntegerField(blank=True, null=True)
    escenario = models.IntegerField(blank=True, null=True)
    numero_individuos = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data'
