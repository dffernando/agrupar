# -*- encoding: utf-8 -*-
from django import forms
from algoritmo.models import * 

class forEscenario1(forms.Form):
	#nombre_escenario1=forms.CharField(max_length=100, label="Nombre del archivo", required=True)
	data_escenario1=forms.FileField(label="Seleccione el archivo", required=True)

class forEscenario2(forms.Form):
	#nombre_escenario2=forms.CharField(max_length=100, label="Nombre del archivo", required=True)
	data_escenario2=forms.FileField(label="Seleccione el archivo", required=True)

class form_select(forms.Form):
	iddata = forms.ModelChoiceField(queryset=Data.objects.all(), label="", initial='', widget=forms.Select(), required=True)
