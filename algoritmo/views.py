# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse
from django.template import RequestContext
from django.template import loader, Context
from StringIO import StringIO
from cStringIO import StringIO
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from algoritmo.models import *
from algoritmo.forms import *
from django.db.models import Count, Avg
import json
import numpy as np
import pandas as pd
import random
import time
#import marshal
# Create your views here.
def index(request):
	if request.method == 'POST':
        # create a form instance and populate it with data from the request:
		form1 = forEscenario1(request.POST, request.FILES)
		form2 = forEscenario2(request.POST, request.FILES)
		form = form_select()
		formato = True
		organizados=True
		comprobar=False
		escenario1=True
		escenario2=True
        # check whether it's valid:
		if form1.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL (opcional)
			formato=comprobar_Formato(request.FILES['data_escenario1'])
			if formato==True:
				comprobar=comprobar_Comillas_Comas(request.FILES['data_escenario1'])
				if comprobar[0]==False:
					separador=comprobar[1]
					handle_uploaded_file(request.FILES['data_escenario1'])
					data1 = pd.read_table('static/csv/data.csv', engine='python', sep=separador)
					data1.to_csv('static/csv/data.csv', index=False)
					data = pd.read_table('static/csv/data.csv', engine='python', sep=',')
					data_comprobar = data[:]
					organizados=comprobar_0_1(data_comprobar, 1)
					if organizados[0]==True:
						n_individuos=organizados[1]
						nombre1=request.FILES['data_escenario1']
						nombre=nombre1.name
						archivo=open('static/csv/data.csv', 'r')
						contenido = archivo.read()
						archivo.close()
						data_comprobacion=comprobar_data(contenido,1)
						if data_comprobacion==True:
							consulta=Data.objects.filter(data=contenido).values("iddata")
							iddata=consulta[0]["iddata"]
							opsion=2
							return HttpResponseRedirect('recuperar/'+str(iddata)+'/'+str(opsion)+'/')
						else:
							nombre_comprobado=comprobar_nombre(nombre)
							nombre_comprobado+=" (Ecs1)"
							f=Data(nombre=nombre_comprobado, data=contenido, 
								comunidades_iniciales=0, escenario=1, 
								numero_individuos=n_individuos)
							f.save()
							consulta=Data.objects.filter(data=contenido).values("iddata")
							iddata=consulta[0]["iddata"]
							opsion=1
							return HttpResponseRedirect('mensaje/'+str(iddata)+'/'+str(opsion)+'/')
					else:
						organizados=organizados[0]
				else:
					comprobar=True
		else:
			escenario1=False
		if form2.is_valid():
			# process the data in form.cleaned_data as required
			# redirect to a new URL (opcional)
			formato=comprobar_Formato(request.FILES['data_escenario2'])
			if formato==True:
				comprobar=comprobar_Comillas_Comas(request.FILES['data_escenario2'])
				if comprobar[0]==False:
					separador=comprobar[1]
					handle_uploaded_file(request.FILES['data_escenario2'])
					data1 = pd.read_table('static/csv/data.csv', engine='python', sep=separador)
					data1.to_csv('static/csv/data.csv', index=False)
					data = pd.read_table('static/csv/data.csv', engine='python', sep=',')
					data_comprobar = data[:]
					organizados=comprobar_0_1(data_comprobar, 2)
					if organizados[0]==True:
						nombre1=request.FILES['data_escenario2']
						nombre=nombre1.name
						archivo=open('static/csv/data.csv', 'r')
						contenido = archivo.read()
						archivo.close()
						data_comprobacion=comprobar_data(contenido,2)
						if data_comprobacion==True:
							consulta=Data.objects.filter(data=contenido).values("iddata")
							iddata=consulta[0]["iddata"]
							opsion=2
							return HttpResponseRedirect('recuperar/'+str(iddata)+'/'+str(opsion)+'/')
						else:
							nombre_comprobado=comprobar_nombre(nombre)
							nombre_comprobado+=" (Ecs2)"
							numero_comunidades_iniciales=organizados[1]
							n_individuos=organizados[2]
							f=Data(nombre=nombre_comprobado, data=contenido, 
										comunidades_iniciales=numero_comunidades_iniciales, 
										escenario=2, numero_individuos=n_individuos)
							f.save()
							consulta=Data.objects.filter(data=contenido).values("iddata")
							iddata=consulta[0]["iddata"]
							opsion=1
							return HttpResponseRedirect('mensaje/'+str(iddata)+'/'+str(opsion)+'/')
					else:
						organizados=organizados[0]
				else:
					comprobar=True
		else:
			escenario2=False
		return render(request, 'index.html', {'form1': form1, 'form2': form2, 
			'formato': formato, 'organizados': organizados, 'comprobar': comprobar, 
			'escenario1': escenario1, 'escenario2': escenario2, 'form': form})
    # if a GET (or any other method) we'll create a blank form
	else:
		form = form_select()
		form1 = forEscenario1()
		form2 = forEscenario2()
		return render(request, 'index.html', {'form1': form1, 'form2': form2, 'form': form})

def handle_uploaded_file(f):
    with open('static/csv/data.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def comprobar_Formato(f):
	nombre=f.name
	separados=nombre.split('.')
	if len(separados)==2:
		if (separados[1]=='csv') or (separados[1]=='data') or( separados[1]=='txt'):
			formato = True
		else:
			formato = False
	else:
		formato = False
	return formato

def comprobar_0_1(data, escenario):
	#escenario 1#
	if escenario==1:
		retornar=[]
		numero_individuos=0
		row=list(data.columns.values)
		columna_0=list(data.loc[:,row[0]])
		ceros_o_unos=[]
		caracteres=[]
		for fila in columna_0:
			if fila==0 or fila==1:
				ceros_o_unos.append(fila)
			if type(fila)==str:
				caracteres.append(fila)

		if len(columna_0)==len(ceros_o_unos):
			numero_individuos=len(row)
			for columna in row:
				columna_data=list(data.loc[:,columna])
				ultima_dato=columna_data[-1]
				if ultima_dato!=0 and ultima_dato!=1:
					organizados=False
					retornar.append(organizados)
					retornar.append(numero_individuos)
					return retornar
				for fila in columna_data:
					if fila!=0 and fila!=1:
						organizados=False
						retornar.append(organizados)
						retornar.append(numero_individuos)
						return retornar
		else:
			if len(columna_0)==len(caracteres):
				data.pop(row[0])
				row=list(data.columns.values)
				numero_individuos=len(row)
				for columna in row:
					columna_data=list(data.loc[:,columna])
					ultima_dato=columna_data[-1]
					if ultima_dato!=0 and ultima_dato!=1:
						organizados=False
						retornar.append(organizados)
						retornar.append(numero_individuos)
						return retornar
					for fila in columna_data:
						if fila!=0 and fila!=1:
							organizados=False
							retornar.append(organizados)
							retornar.append(numero_individuos)
							return retornar
				
			else:
				organizados=False
				retornar.append(organizados)
				retornar.append(numero_individuos)
				return retornar
		organizados=True
		retornar.append(organizados)
		retornar.append(numero_individuos)
		return retornar
	#escenario 2#
	else:
		retornar=[]
		comunidades_iniciales_lista=[]
		comunidades_iniciales_numero=0
		numero_individuos=0
		row=list(data.columns.values)
		columna_0=list(data.loc[:,row[0]])
		ceros_o_unos=[]
		caracteres=[]
		for fila in columna_0:
			if (fila==0 or fila==1) or (fila=="0" or fila=="1"):
				ceros_o_unos.append(fila)
			if type(fila)==str:
				caracteres.append(fila)

		if (len(columna_0)-1==len(ceros_o_unos)) or (len(columna_0)-1==len(ceros_o_unos)-1):
			numero_individuos=len(row)
			for columna in row:
				columna_data=list(data.loc[:,columna])
				solonumero=columna_data[0:-1]
				for fila in solonumero:
					if (fila!=0 and fila!=1) and (fila!="0" and fila!="1"):
						organizados=False
						retornar.append(organizados)
						retornar.append(comunidades_iniciales_numero)
						retornar.append(numero_individuos)
						return retornar
				comunidades_iniciales_lista.append(columna_data[-1])
		else:
			if len(columna_0)-1==len(caracteres):
				data.pop(row[0])
				row=list(data.columns.values)
				numero_individuos=len(row)
				ceros=[]
				unos=[]
				diferentes=[]
				for columna in row:
					columna_data=list(data.loc[:,columna])
					solonumero=columna_data[0:-1]
					for fila in solonumero:
						if (fila!=0 and fila!=1) and (fila!="0" and fila!="1"):
							organizados=False
							retornar.append(organizados)
							retornar.append(comunidades_iniciales_numero)
							retornar.append(numero_individuos)
							return retornar
					comunidades_iniciales_lista.append(columna_data[-1])

			else:
				organizados=False
				retornar.append(organizados)
				retornar.append(comunidades_iniciales_numero)
				retornar.append(numero_individuos)
				return retornar
		comunidades_iniciales_no_repetidos=set(comunidades_iniciales_lista)
		comunidades_iniciales_numero=len(comunidades_iniciales_no_repetidos)
		organizados=True
		retornar.append(organizados)
		retornar.append(comunidades_iniciales_numero)
		retornar.append(numero_individuos)
		return retornar 

def comprobar_data(contenido, escena):
	consulta=Data.objects.filter(data=contenido, escenario=escena).count()
	if consulta==0:
		data_comprobacion=False
	else:
		data_comprobacion=True
	return data_comprobacion

def comprobar_nombre(nombre):
	consulta=Data.objects.filter(nombre__startswith=nombre).count()
	if consulta==0:
		return nombre
	else:
		nombre1=nombre+str(consulta)
		return nombre1

def comprobar_Comillas_Comas(file):
	retornar=[]
	comprobar=False
	separador=""
	for fila in file:
		contador_comas=0
		dos_puntos=0
		tabulador=0
		puto_y_coma=0
		for campo in fila:
			if campo==",":
				contador_comas+=1
			if campo==":":
				dos_puntos+=1
			if campo=="	":
				tabulador+=1
			if campo==";":
				puto_y_coma+=1
			if campo=='"' or campo=="'":
				comprobar=True
				retornar.append(comprobar)
				retornar.append(separador)
				return retornar
		if contador_comas==0 and dos_puntos==0 and tabulador==0 and puto_y_coma==0:
			comprobar=True
			retornar.append(comprobar)
			retornar.append(separador)
			return retornar
		else:
			if contador_comas!=0 and dos_puntos==0 and tabulador==0 and puto_y_coma==0:
				separador="," 
			else:
				if contador_comas==0 and dos_puntos!=0 and tabulador==0 and puto_y_coma==0:
					separador=":"
				else:
					if contador_comas==0 and dos_puntos==0 and tabulador!=0 and puto_y_coma==0:
						separador="	"
					else:
						if contador_comas==0 and dos_puntos==0 and tabulador==0 and puto_y_coma!=0:
							separador=";"
						else:
							comprobar=True
							retornar.append(comprobar)
							retornar.append(separador)
							return retornar
	retornar.append(comprobar)
	retornar.append(separador)
	return retornar

#def Inicio(contenido, escenario, data_tabla):
def Inicio(iddata, opsion):
	consulta=Data.objects.filter(iddata=iddata).values("escenario", "data", "numero_individuos")
	contenido=consulta[0]["data"]
	escenario=consulta[0]["escenario"]
	n_individuos=consulta[0]["numero_individuos"]
	archivo=open('static/csv/data.csv', 'w')
	archivo.write(contenido)
	archivo.close()
	data_tabla = pd.read_table('static/csv/data.csv', engine='python', sep=',')
	if escenario==1:
		if n_individuos<=20:
			vueltas=5
		else:
			if n_individuos>20 and n_individuos<=35:
				vueltas=50
			else:
				if n_individuos>35 and n_individuos<=75:
					vueltas=100
				else:
					if n_individuos>75 and n_individuos<=150:
						vueltas=150
					else:
						if n_individuos>150 and n_individuos<=500:
							vueltas=300
						else:
							vueltas=500
		row=list(data_tabla.columns.values)
		columna_0=list(data_tabla.loc[:,row[0]])
		caracteres=[]
		for fila in columna_0:
			if type(fila)==str:
				caracteres.append(fila)
		if len(columna_0)==len(caracteres):
			data_tabla.pop(row[0])
			Combinaciones_bucle(data_tabla, escenario, iddata, vueltas, opsion)
		else:
			Combinaciones_bucle(data_tabla, escenario, iddata, vueltas, opsion)
		#reenviar(iddata)

	if escenario==2:
		if n_individuos<=200:
			vueltas=20
		else:
			vueltas=500
		row=list(data_tabla.columns.values)
		columna_0=list(data_tabla.loc[:,row[0]])
		ceros_o_unos=[]
		caracteres=[]
		for fila in columna_0:
			if (fila==0 or fila==1) or (fila=="0" or fila=="1"):
				ceros_o_unos.append(fila)
			if type(fila)==str:
				caracteres.append(fila)

		if len(columna_0)-1==len(caracteres):
			data_tabla.pop(row[0])
			Combinaciones_bucle(data_tabla, escenario, iddata, vueltas, opsion)
		else:
			Combinaciones_bucle(data_tabla, escenario, iddata, vueltas, opsion)

def Combinaciones_bucle(data, escenario, iddata, vueltas, opsion):
	if escenario==1:
		lista=[0.2,0.3,0.4,0.5,0.6]
		#Escenario1(0.3, 0.3, data, iddata)
		for i in lista:
			umbral2=i
			for j in lista:
				k2=j
				Escenario1(umbral2, k2, data, iddata, vueltas, opsion)
	if escenario==2:
		lista=[0.2,0.3,0.4,0.5,0.6]
		#Escenario1(0.3, 0.3, data, iddata)
		for i in lista:
			umbral2=i
			for j in lista:
				umbral1=j
				for x in lista:
					k2=x
					for y in lista:
						k1=y
						Escenario2(umbral2, umbral1, k2, k1, data, iddata, vueltas, opsion)

# CREA COMUNIDADES CUANDO NO HAY COMUNIDADES 
def Escenario1(umbral2, k2, data, iddata, vueltas, opsion):
#	umbral2=0.6 #depósito
#	k2=0.6 #depósito
	k1=0.0 #recolección
	umbral1=0.0 #recoleccion
	##crea las comunidades en un supuesto que no hay comuniddes
	##en un principio
	comunidades_creadas=crearComunidades(data, umbral2, k2)
	comunidades=comunidades_creadas[0]
	patrones=comunidades_creadas[1]

	if opsion==3:
		fusion=fusionarComunidadesPropuesta(comunidades, patrones, umbral2, k2, k1, umbral1, vueltas)
		comunidades=[]
		patrones=[]
		comunidades=fusion[0]
		patrones=fusion[1]
	else:
		fusion=fusionarComunidades(comunidades, patrones, umbral2, k2, k1, umbral1, vueltas)
		comunidades=[]
		patrones=[]
		comunidades=fusion[0]
		patrones=fusion[1]

	if len(comunidades)>0:
		##calculo de las métricas de cohesión y separación 
		##cohesión
		cohesion=Cohesion(comunidades, patrones)
		#print cohesion, "cohesión"

		##separación
		separacion=Separacion(patrones, comunidades)

		if opsion==3:
			##guardar la combinación en la base de datos 
			c=Combinaciones(k1=k1, k2=k2, umbral1=umbral1, umbral2=umbral2, 
				cohesion=cohesion, separacion=separacion, 
				numero_comunidades_finales=len(comunidades), 
				data_iddata=Data.objects.get(iddata=iddata), solucion=1)
			c.save()

			##obtengo el id de la combinación
			consulta=Combinaciones.objects.filter(k1=k1, k2=k2, umbral1=umbral1, 
				umbral2=umbral2, data_iddata=iddata, solucion=1).values("idcombinaciones")
			idcombinaciones=consulta[0]['idcombinaciones']
			Guardar_comunidades(comunidades, idcombinaciones)
		else:
			##guardar la combinación en la base de datos 
			c=Combinaciones(k1=k1, k2=k2, umbral1=umbral1, umbral2=umbral2, 
				cohesion=cohesion, separacion=separacion, 
				numero_comunidades_finales=len(comunidades), 
				data_iddata=Data.objects.get(iddata=iddata), solucion=0)
			c.save()

			##obtengo el id de la combinación
			consulta=Combinaciones.objects.filter(k1=k1, k2=k2, umbral1=umbral1, 
				umbral2=umbral2, data_iddata=iddata, solucion=0).values("idcombinaciones")
			idcombinaciones=consulta[0]['idcombinaciones']
			Guardar_comunidades(comunidades, idcombinaciones)
	else:
		c=Combinaciones(k1=k1, k2=k2, umbral1=umbral1, umbral2=umbral2,cohesion=0, 
			separacion=0, numero_comunidades_finales=0,
			data_iddata=Data.objects.get(iddata=iddata))
		c.save()

#CREA COMUNIDADES CUANDO HAY COMUNIDADES 
def Escenario2(umbral2, umbral1, k2, k1, data, iddata, vueltas, opsion): 

	##reajusta las comunidades entrantes
	reajuste=reajustarComunidades(data, k1, k2, umbral1, umbral2)
	comunidades=reajuste[0]
	patrones=reajuste[1]
	comunidadesEntrantesIniciales=reajuste[2]

	if opsion==3:
		fusion=fusionarComunidadesPropuesta(comunidades, patrones, umbral2, k2, k1, umbral1, vueltas)
		comunidades=[]
		patrones=[]
		comunidades=fusion[0]
		patrones=fusion[1]
	else: 
		##fusion de las comunidades creadas
		fusion=fusionarComunidades(comunidades, patrones, umbral2, k2, k1, umbral1, vueltas)
		comunidades=[]
		patrones=[]
		comunidades=fusion[0]
		patrones=fusion[1]

	if len(comunidades)>0:
		##calculo de las métricas de cohesión y separación 
		##cohesión
		cohesion=Cohesion(comunidades, patrones)

		##separación
		separacion=Separacion(patrones, comunidades)

		if opsion==3:
			##guardar la combinación en la base de datos 
			c=Combinaciones(k1=k1, k2=k2, umbral1=umbral1, umbral2=umbral2, 
				cohesion=cohesion, separacion=separacion, 
				numero_comunidades_finales=len(comunidades), 
				data_iddata=Data.objects.get(iddata=iddata), solucion=1)
			c.save()

			##obtengo el id de la combinación
			consulta=Combinaciones.objects.filter(k1=k1, k2=k2, umbral1=umbral1, 
				umbral2=umbral2, data_iddata=iddata, solucion=1).values("idcombinaciones")
			idcombinaciones=consulta[0]['idcombinaciones']
			Guardar_comunidades(comunidades, idcombinaciones)
		else:
			##guardar la combinación en la base de datos 
			c=Combinaciones(k1=k1, k2=k2, umbral1=umbral1, umbral2=umbral2, 
				cohesion=cohesion, separacion=separacion, 
				numero_comunidades_finales=len(comunidades), 
				data_iddata=Data.objects.get(iddata=iddata), solucion=0)
			c.save()

			##obtengo el id de la combinación
			consulta=Combinaciones.objects.filter(k1=k1, k2=k2, umbral1=umbral1, 
				umbral2=umbral2, data_iddata=iddata, solucion=0).values("idcombinaciones")
			idcombinaciones=consulta[0]['idcombinaciones']
			Guardar_comunidades(comunidades, idcombinaciones)
		
	else:
		c=Combinaciones(k1=k1, k2=k2, umbral1=umbral1, umbral2=umbral2, 
			cohesion=0, separacion=0, 
			numero_comunidades_finales=0, 
			data_iddata=Data.objects.get(iddata=iddata))
		c.save()

#CALCULAR EL PATRON DE LA COMUNIDAD
def calcularPatron(comunidad):
	dimesion=comunidad.shape
	if dimesion[1]==1:
		return comunidad
	else:
		row=list(comunidad.columns.values)
		individuoComunidad=[]
		for i in row:
			if len(individuoComunidad)==0:
				individuoComunidad=list(comunidad.loc[:,i])
			else:
				multiplicacion=[]
				individuo=list(comunidad.loc[:,i])
				for t, r in zip(individuoComunidad, individuo):
					multiplicacion.append(t*r)
				individuoComunidad=multiplicacion
		patron=pd.DataFrame(data=individuoComunidad, columns=["p"])
		return patron

#COMPARO EL NUEVO ESTUDIANTE CON CADA PATRON DE CADA COMUNIDAD
def comparar(individuo, patron):
	
	comparar=[]
	for e, p in zip(individuo, patron):
		if e==p:
			comparar.append(0)
		else:
			comparar.append(1)

	suma=0
	for i in comparar:
		suma+=i
	return suma

#DEPOSITA EL NUEVO ESTUDIANTE EN LA COMUNIDAD
def Union(individuo, comunidad):
	#print '============================================================'
	#print estudiante
	#print '============================================================'
	#print comunidad
	#print '============================================================'
	datos_unidos = individuo.join(comunidad)
	return datos_unidos

#AJUSTA LAS COMUNIDADES
def ajustarComunidad(patrones, k2, umbral2, ajustar):
	ajustar=False
	retornar=[]

	c=0
	while c<len(patrones):
		igualcero=[]
		diferentecero=[]
		row=list(patrones[c].columns.values)
		primerPatron=list(patrones[c].loc[:,row[0]])

		cont=c+1
		while cont<len(patrones):
			row1=list(patrones[cont].columns.values)
			siguientePatron=list(patrones[cont].loc[:,row1[0]])
			resultado=comparar(primerPatron, siguientePatron)

			if resultado==0:
				igualcero.append(cont)
			else:
				d=distancia(resultado)
				Pd=posivilidadDeposito(d, k2)

				if (Pd > umbral2):
					diccionario={}
					diccionario['posicion']=cont
					diccionario['pd']=Pd
					diferentecero.append(diccionario)
			cont+=1

		if len(igualcero)==0:

			if len(diferentecero)!=0:
				maximo=max(diferentecero)
				aleatorio=[]

				for y in diferentecero:

					if y['pd']==maximo['pd']:
						aleatorio.append(y['posicion'])

				a=random.sample(aleatorio,1)
				#print diferentecero
				#print aleatorio,"maximo"
				#print a, "ajustar comunidad random>u2"
				ajustar=True
				retornar.append(c)
				retornar.append(a[0])
				retornar.append(ajustar)
				return retornar
		else:
		#if len(igualcero)!=0:
			ajustar=True
			retornar.append(c)
			posicion=random.sample(igualcero,1)
			#print igualcero
			#print posicion,"ajustar comunidad random=ceros"
			retornar.append(posicion[0])
			#retornar=igualcero
			retornar.append(ajustar)
			return retornar

		c+=1

	retornar.append(ajustar)
	return retornar

#COMPARA EL NUEVO ESTUDIANTE CON CADA PATRON
def ajustarIndividuo(umbral2, k2, nuevoIndividuo, patrones):
	#print len(patrones), "tamaño de la tabla patrones"
	contador=0
	retornar=[]
	igualcero=[]
	diferentecero=[]
	for i in patrones:
		retornar=[]
		row=list(i.columns.values)
		patron=list(i.loc[:,row[0]])
		#print nuevoEstudiante, "nuevo estudiante"
		#print patron, "patron", contador
		suma=comparar(nuevoIndividuo, patron)
		if suma==0:
			#retornar.append(contador)
			#print "empezar de nuevo suma=0",suma
			#return retornar
			#diccionario={}
			#diccionario['modelo']=d['modelo']
			igualcero.append(contador)

		else:
			d=distancia(suma)
			Pd=posivilidadDeposito(d, k2)
			if Pd>umbral2:
				diccionario={}
				diccionario['posicion']=contador
				diccionario['pd']=Pd
				diferentecero.append(diccionario)
				#print "empezar de nuevo Pd>umbral2", "Pd=", Pd, "umbral2=", umbral2
				#return retornar
		contador+=1
		#print "siguiente bucle"
	if len(igualcero)==0:
		if len(diferentecero)==0:
			return retornar
		else:
			maximo=max(diferentecero)
			aleatorio=[]
			for y in diferentecero:
				if y['pd']==maximo['pd']:
					aleatorio.append(y['posicion'])
			#print "cumple la condicion"
			a=random.sample(aleatorio,1)
			#print diferentecero
			#print aleatorio,"maximo"
			#print a,"ajustar estudiante random>u2"
			#print a, aleatorio
			retornar.append(a[0])
			return retornar
	else:
		#print "hay ceros"
		posicion=random.sample(igualcero,1)
		#print igualcero
		#print posicion,"ajustar estudiante random=ceros"
		#print posicion, igualcero
		#retornar.append(posicion)
		retornar=posicion
		return retornar		

#CALCULA LA DISTANCIA (d)
def distancia(suma):
	d=1/float(suma)
	return d

#CALCULA LA POSIVILIDAD DE DEPOSITO (Pd)
def posivilidadDeposito(d, k2):
	#Pd=(f/float(k2+f))**2
	#Pd=(d/float(k2+d))**2
	Pd=d/float(k2+d)
	return Pd


#CALCULA LA POSIVILIDAD DE RECOLECCIÓN (Pr)
def posivilidadRecoleccion(d, k1):
	#Pr=(k1/float(k1+f))**2
	#Pr=(k1/float(k1+d))**2
	Pr=k1/float(k1+d)
	return Pr

#CREA COMUNIDADES CUANDO NO HAY COMUNIDADES CREADAS EN UN PRINCIPIO
def crearComunidades(data, umbral2, k2):
	comunidades=[]
	patrones=[]
	retornar=[]
	individuos=list(data.columns.values)
	#---recorro cada columna de la matriz
	for e in individuos:
		if len(comunidades)==0:
			comunidad = pd.DataFrame(data.loc[:,e], columns=[e])
			comunidades.append(comunidad)
			#posicion=len(comunidades)
			patron=calcularPatron(comunidad)
			patrones.append(patron)
		else:
			#print posicion
			nuevoIndividuo=list(data.loc[:,e])
			ajustar=ajustarIndividuo(umbral2, k2, nuevoIndividuo, patrones)
			if len(ajustar)>0:
				posicion=ajustar[0]
				#print posicion
				nuevoIndividuo = pd.DataFrame(data.loc[:,e], columns=[e])
				union=Union(nuevoIndividuo, comunidades[posicion])
				comunidades[posicion]=union
				patron=calcularPatron(union)
				patrones[posicion]=patron
			else:
				comunidad = pd.DataFrame(data.loc[:,e], columns=[e])
				comunidades.append(comunidad)
				patron=calcularPatron(comunidad)
				patrones.append(patron)

	retornar.append(comunidades)
	retornar.append(patrones)

	return retornar

#RECOLECTA LOS INDIVIDUOS QUE SUPERAN EL UMBRAL1 EN LA UNIÓN
def recolectarIndividuosUnion(patron_union, union, comunidades, patrones, k1, umbral1):
	retornar=[]
	individuosmovidos=[]
	columna=list(patron_union.columns.values)
	patron_lista=list(patron_union.loc[:,columna[0]])
	row=list(union.columns.values)
	columnas_a_moverse=[]
	for r in row:
		individuo=list(union.loc[:,r])
		resultado=comparar(patron_lista, individuo)
		if resultado!=0:
			d=distancia(resultado)
			Pr=posivilidadRecoleccion(d, k1)

			if Pr>umbral1:
				columnas_a_moverse.append(r)
				tabla=pd.DataFrame(data=individuo, columns=[r])

				if len(individuosmovidos)==0:
					individuosmovidos.append(tabla)
				else:
					fusion=Union(individuosmovidos[0], tabla)
					individuosmovidos[0]=fusion
							
	print union, "comunidades con los estudiantes mal ubicados "

	#if (sorted(row)!=sorted(columnas_a_moverse) 
	#	and sorted(columnas_a_moverse)!=sorted(comunidad_primera_actual) 
	#	and sorted(columnas_a_moverse)!=sorted(comunidad_segunda_actual) 
	#	and len(columnas_a_moverse)!=0):
	if (sorted(row)!=sorted(columnas_a_moverse) 
	and len(columnas_a_moverse)!=0):

		for y in columnas_a_moverse:
			union.pop(y)
		patron_final=calcularPatron(union)
		comunidades.append(union)
		patrones.append(patron_final)

	#else:
	if len(columnas_a_moverse)==0:
		comunidades.append(union)
		patrones.append(patron_union)
		individuosmovidos=[]

	print union, "comunidades menos los estudiantes mal ubicados "
	print columnas_a_moverse, "columnas a moverse"
		#c+=1
	##___________________________________________________
	print individuosmovidos, "estudiantes movidos"

	retornar.append(individuosmovidos)
	retornar.append(comunidades)
	retornar.append(patrones)
	return retornar

#DEPOSITO LOS INDIVIDUOS MOVIDOS EN LAS COMUNIDADES QUE SUPEREN EL UMBRAL 2
def depositarIndividuo(individuosmovidos, comunidades, patrones, umbral2, k2):
	retornar=[]
	individuos=list(individuosmovidos[0].columns.values)
	#---recorro cada columna de la matriz
	for e in individuos:
		nuevoIndividuo=list(individuosmovidos[0].loc[:,e])
		ajustar=ajustarIndividuo(umbral2, k2, nuevoIndividuo, patrones)
		if len(ajustar)>0:
			posicion=ajustar[0]
			#comunidad=comunidades[posicion]
			nuevoIndividuo = pd.DataFrame(individuosmovidos[0].loc[:,e], columns=[e])
			#print nuevoEstudiante, "nuevo estudiantes"
			#print comunidad, "comunidad"
			union=Union(nuevoIndividuo, comunidades[posicion])
			comunidades[posicion]=union
			patron=calcularPatron(union)
			patrones[posicion]=patron
		else:
			comunidad = pd.DataFrame(individuosmovidos[0].loc[:,e], columns=[e])
			comunidades.append(comunidad)
			patron=calcularPatron(comunidad)
			patrones.append(patron)

	retornar.append(comunidades)
	retornar.append(patrones)
	return retornar

#SE COMPARA LOS PATRONES DE LAS COMUNIDADES PARA FUSIONARLAS
def fusionarComunidades(comunidades, patrones, umbral2, k2, k1, umbral1, vueltas):
	retornar=[]
	continuar=True
	comunidades_comparar=[]
	numero_comunidades_fusion=[]
	comunidades_historial=[]
	#patrones_fusion=[]
	mientras=0
	repetidas_c=0
	minimo=0
	minimos=[]
	#fusion_patron_c=0
	while continuar==True:

		diccionario={}
		historial={}
		ajustar=ajustarComunidad(patrones, k2, umbral2, continuar)
		if len(ajustar)>1:

			#print ajustar
			primer=ajustar[0]
			segundo=ajustar[1]
			continuar=ajustar[2]

			#print comunidades[primer], "primera comunidad"
			#print comunidades[segundo], "segunda comunidad"
			#print primer, segundo, "primera y segunda posición"
			#print len(comunidades), "tamaño de comunidades"

			union=Union(comunidades[primer], comunidades[segundo])

			union_actual=list(union.columns.values)
			diccionario["union_anterior"]=union_actual

			#print union, "union"
			comunidades.pop(primer)
			comunidades.pop(segundo-1)
			#comunidades.append(union)
			#patron_union=calcularPatron(union)
			#print patron_union, "patron de union"
			patrones.pop(primer)
			patrones.pop(segundo-1)
			#patrones.append(patron)
			comunidades_repetidas=[]

			if len(comunidades_comparar)!=0:

				#comunidades_repetidas=[]

				for y in comunidades_comparar:

					#print sorted(union_actual), "union actual"
					#print sorted(y["union_anterior"]), "union anterior"
					if sorted(union_actual)==sorted(y["union_anterior"]):
						#print sorted(union_actual), "union actual"
						#print sorted(y["union_anterior"]), "union anterior"
						comunidades_repetidas.append(sorted(y["union_anterior"]))
						repetidas_c+=1

				#print len(comunidades_repetidas), "tamaño de las comunidades repetidas"
				#print comunidades_repetidas, "comunidades repetidas"
				#print repetidas_c, "repetidas contador"

				if len(comunidades_repetidas)<=5:

					##verificar si cada estudiante pertenece a cada comunidad
					##Y muevo los estudiantes que no pertenecen a la comunidad
					#recoleccion=recolectarIndividuosUnion(patron_union, union, comunidades, patrones, k1, umbral1)
					#individuosmovidos=recoleccion[0]
					individuosmovidos=[]
					individuosmovidos.append(union)
					#comunidades=[]
					#patrones=[]
					#comunidades=recoleccion[1]
					#patrones=recoleccion[2]

				else:
					#if len(comunidades_repetidas)>0 and len(comunidades_repetidas)<=2:
					#comunidades.append(union)
					#patrones.append(patron_union)
					individuosmovidos=[]
					continuar=False
					#individuosmovidos.append(union)
					comunidades=[]
					patrones=[]
					#	print "repetidas una o dos vez"
					#else:
					#	individuosmovidos=[]
					#	individuosmovidos.append(union)
					#	print "repetidas más de dos vez"
			else:
				##verificar si cada estudiante pertenece a cada comunidad
				##Y muevo los estudiantes que no pertenecen a la comunidad
				#recoleccion=recolectarIndividuosUnion(patron_union, union, comunidades, patrones, k1, umbral1)
				#individuosmovidos=recoleccion[0]
				#comunidades=[]
				#patrones=[]
				#comunidades=recoleccion[1]
				#patrones=recoleccion[2]
				individuosmovidos=[]
				individuosmovidos.append(union)
				
			##a cada estudiante movido se lo compara con los patrones de las comunidades 
			##resultantes para saber si se los asigna a alguna comunidad o se crea una
			if len(individuosmovidos)!=0:
				depositos=depositarIndividuo(individuosmovidos, comunidades, patrones, umbral2, k2)
				comunidades=[]
				patrones=[]
				comunidades=depositos[0]
				patrones=depositos[1]

			mientras+=1
			numero_comunidades_fusion.append(len(comunidades))
			comunidades1 = comunidades[:]
			patrones1 = patrones[:]
			historial["comunidad"]=comunidades1
			historial["patron"]=patrones1
			comunidades_historial.append(historial)
			#patrones_fusion.append(patrones)
			comunidades_comparar.append(diccionario)

			if minimo==0:
				minimo=min(numero_comunidades_fusion)
				minimos.append(minimo)

			if mientras==vueltas:
				mientras=0
				#if minimo==0:
				#	minimo=min(numero_comunidades_fusion)
				#	minimos.append(minimo)
				#else:
				minimo1=min(numero_comunidades_fusion)
				if minimo1>=minimo:
					minimos.append(minimo1)
					posicion_minimo=numero_comunidades_fusion.index(minimo)
					patrones=[]
					comunidades=[]
					#comunidades=comunidades_historial[posicion_minimo]["comunidad"]
					#patrones=comunidades_historial[posicion_minimo]["patron"]
					#print minimo, "minimo"
					#print minimos, "minimos"
					#print numero_comunidades_fusion, "numero comunidades fusion"
					#print len(numero_comunidades_fusion), "numero comunidades fusion"
					#print len(comunidades_historial), "historial comunidades"
					continuar=False
				else:
					minimo=min(numero_comunidades_fusion)
					minimos.append(minimo)

		else:
			continuar=ajustar[0]

		#print numero_comunidades_fusion, "numero de comunidades buscando patron"
		#print continuar

	retornar.append(comunidades)
	retornar.append(patrones)
	return retornar

def fusionarComunidadesPropuesta(comunidades, patrones, umbral2, k2, k1, umbral1, vueltas):
	retornar=[]
	continuar=True
	comunidades_comparar=[]
	numero_comunidades_fusion=[]
	comunidades_historial=[]
	#patrones_fusion=[]
	mientras=0
	repetidas_c=0
	minimo=0
	minimos=[]
	#fusion_patron_c=0
	while continuar==True:

		diccionario={}
		historial={}
		ajustar=ajustarComunidad(patrones, k2, umbral2, continuar)
		if len(ajustar)>1:

			#print ajustar
			primer=ajustar[0]
			segundo=ajustar[1]
			continuar=ajustar[2]

			#print comunidades[primer], "primera comunidad"
			#print comunidades[segundo], "segunda comunidad"
			#print primer, segundo, "primera y segunda posición"
			#print len(comunidades), "tamaño de comunidades"

			union=Union(comunidades[primer], comunidades[segundo])

			union_actual=list(union.columns.values)
			diccionario["union_anterior"]=union_actual

			#print union, "union"
			comunidades.pop(primer)
			comunidades.pop(segundo-1)
			#comunidades.append(union)
			#patron_union=calcularPatron(union)
			#print patron_union, "patron de union"
			patrones.pop(primer)
			patrones.pop(segundo-1)
			#patrones.append(patron)
			comunidades_repetidas=[]

			if len(comunidades_comparar)!=0:

				#comunidades_repetidas=[]

				for y in comunidades_comparar:

					#print sorted(union_actual), "union actual"
					#print sorted(y["union_anterior"]), "union anterior"
					if sorted(union_actual)==sorted(y["union_anterior"]):
						#print sorted(union_actual), "union actual"
						#print sorted(y["union_anterior"]), "union anterior"
						comunidades_repetidas.append(sorted(y["union_anterior"]))
						repetidas_c+=1

				#print len(comunidades_repetidas), "tamaño de las comunidades repetidas"
				#print comunidades_repetidas, "comunidades repetidas"
				#print repetidas_c, "repetidas contador"

				if len(comunidades_repetidas)<=5:

					##verificar si cada estudiante pertenece a cada comunidad
					##Y muevo los estudiantes que no pertenecen a la comunidad
					#recoleccion=recolectarIndividuosUnion(patron_union, union, comunidades, patrones, k1, umbral1)
					#individuosmovidos=recoleccion[0]
					individuosmovidos=[]
					individuosmovidos.append(union)
					#comunidades=[]
					#patrones=[]
					#comunidades=recoleccion[1]
					#patrones=recoleccion[2]

				else:
					#if len(comunidades_repetidas)>0 and len(comunidades_repetidas)<=2:
					#comunidades.append(union)
					#patrones.append(patron_union)
					individuosmovidos=[]
					continuar=False
					individuosmovidos.append(union)
					#comunidades=[]
					#patrones=[]
					#	print "repetidas una o dos vez"
					#else:
					#	individuosmovidos=[]
					#	individuosmovidos.append(union)
					#	print "repetidas más de dos vez"
			else:
				##verificar si cada estudiante pertenece a cada comunidad
				##Y muevo los estudiantes que no pertenecen a la comunidad
				#recoleccion=recolectarIndividuosUnion(patron_union, union, comunidades, patrones, k1, umbral1)
				#individuosmovidos=recoleccion[0]
				#comunidades=[]
				#patrones=[]
				#comunidades=recoleccion[1]
				#patrones=recoleccion[2]
				individuosmovidos=[]
				individuosmovidos.append(union)
				
			##a cada estudiante movido se lo compara con los patrones de las comunidades 
			##resultantes para saber si se los asigna a alguna comunidad o se crea una
			if len(individuosmovidos)!=0:
				depositos=depositarIndividuo(individuosmovidos, comunidades, patrones, umbral2, k2)
				comunidades=[]
				patrones=[]
				comunidades=depositos[0]
				patrones=depositos[1]

			mientras+=1
			numero_comunidades_fusion.append(len(comunidades))
			comunidades1 = comunidades[:]
			patrones1 = patrones[:]
			historial["comunidad"]=comunidades1
			historial["patron"]=patrones1
			comunidades_historial.append(historial)
			comunidades_comparar.append(diccionario)

			if len(comunidades_repetidas)>5:
				minimo=min(numero_comunidades_fusion)
				posicion_minimo=numero_comunidades_fusion.index(minimo)
				patrones=[]
				comunidades=[]
				comunidades=comunidades_historial[posicion_minimo]["comunidad"]
				patrones=comunidades_historial[posicion_minimo]["patron"]

			if minimo==0:
				minimo=min(numero_comunidades_fusion)
				minimos.append(minimo)

			if mientras==vueltas:
				mientras=0
				minimo1=min(numero_comunidades_fusion)
				if minimo1>=minimo:
					minimos.append(minimo1)
					posicion_minimo=numero_comunidades_fusion.index(minimo)
					patrones=[]
					comunidades=[]
					comunidades=comunidades_historial[posicion_minimo]["comunidad"]
					patrones=comunidades_historial[posicion_minimo]["patron"]
					continuar=False
				else:
					minimo=min(numero_comunidades_fusion)
					minimos.append(minimo)

		else:
			continuar=ajustar[0]

	retornar.append(comunidades)
	retornar.append(patrones)
	return retornar

#CALCULO DE LA METRICA COHESION
def Cohesion(comunidades, patrones):
	sumaTotal=0
	#contador=0
	for y, c in zip(patrones, comunidades):
		sumaComunidad=0
		cabecera=list(y.columns.values)
		patron=list(y.loc[:,cabecera[0]])
		#print columna, patron
		row=list(c.columns.values)
		for e in row:
			#print e
			estudiante=list(c.loc[:,e])
			#print estudiante, patron
			valor=comparar(patron, estudiante)
			#contador+=1
			#print valor
			sumaComunidad+=valor
		#sumaComunidadPromedio=sumaComunidad/float(len(row))
		sumaTotal+=sumaComunidad/float(len(row))
		#sumaTotal+=sumaComunidad
	#print sumaTotal
	#print len(comunidades), len(patrones)
	cohesion=sumaTotal/float(len(comunidades))
	#cohesion=sumaTotal
	#cohesion=sumaTotal/float(contador)
	#cohesion2=(cohesion+len(comunidades))*0.1
	return cohesion

#CALCULO DE LA METRICA SEPARACION
def Separacion(patrones, comunidades):
	c=0
	suma=0
	contador=0
	#print patrones, "patrones"
	#print comunidades, "comunidades"
	while c<len(patrones):
		cabecera=list(patrones[c].columns.values)
		patron1=list(patrones[c].loc[:,cabecera[0]])
		cont=c+1
		while cont<len(patrones):
			#print "primer patron", patron1, "posicion", c
			cabecera1=list(patrones[cont].columns.values)
			patron2=list(patrones[cont].loc[:,cabecera1[0]])
			#print "segundo patron", patron2, "posicion", cont
			valor=comparar(patron1, patron2)
			contador+=1
			suma+=valor
			cont+=1
		#print cont, "cont"
	 	c+=1 
	#print contador
	if len(comunidades)==1:
		separacion=0
		#print "cero"
	else:
		separacion=suma/float(contador)
		#separacion=(separacion+len(comunidades))*0.1
		#print "división"
		#separacion2=suma/float(len(comunidades))
		#separacion=(separacion2+len(comunidades))*0.1
	return separacion

#ORDENAR EN UNA LISTA LAS COMUNIDADES ENTRANTES
def ordenarListaComunidadesEntrantes(data):
	retornar=[]
	comunidadesEntrantesIniciales=[]
	comunidades=[]
	patrones=[]
	grupos=list(set(data.iloc[-1]))
	#print grupos
	individuos=list(data.columns.values)
	#print estudiantes

	##guardo las comunidades en una lista
	for y in grupos:
		#print y
		comunidad=[]
		for e in individuos:
			#print e
			individuo = pd.DataFrame(data.loc[:,e], columns=[e])
			#print estudiante
			grupo=list(individuo.iloc[-1])
			#print grupo[0]
			if y==grupo[0] and len(comunidad)==0:
				solonumero=individuo[0:-1]
				comversion=list(solonumero.loc[:,e])
				tabla=pd.DataFrame(comversion, columns=[e], dtype=int)
				comunidad=tabla
				#print comunidad
			else:
				if y==grupo[0] and len(comunidad)!=0:
					#print comunidad[0]
					solonumero=individuo[0:-1]
					comversion=list(solonumero.loc[:,e])
					tabla=pd.DataFrame(comversion, columns=[e], dtype=int)
					union=Union(comunidad, tabla)
					comunidad=union
		#print comunidad.dtypes
		comunidades.append(comunidad)
		comunidadesEntrantesIniciales.append(comunidad)
	#print comunidades, "comunidades iniciales"

	## obtener el patron de cada comunidad
	for y in comunidades:
		#print y
		patron=calcularPatron(y)
		patrones.append(patron)
	#print comunidades[4], patrones[4]

	retornar.append(comunidadesEntrantesIniciales)
	retornar.append(comunidades)
	retornar.append(patrones)
	return retornar

#VERIFICAR SI LOS INDIVIDUOS ESTAN BIEN UBICADOS EN LAS COMUNIDADES
def recolectarIndividuo(comunidades, patrones, k1, umbral1):
	retornar=[]
	c=0
	individuosmovidos=[]
	comunidades_a_eliminarse=[]
	while c<len(patrones):
		columna=list(patrones[c].columns.values)
		patron=list(patrones[c].loc[:,columna[0]])
		row=list(comunidades[c].columns.values)
		columnas_a_moverse=[]
		for r in row:
			individuo=list(comunidades[c].loc[:,r])
			resultado=comparar(patron, individuo)
			if resultado!=0:
				d=distancia(resultado)
				Pr=posivilidadRecoleccion(d, k1)
				if Pr>umbral1:
					columnas_a_moverse.append(r)
					tabla=pd.DataFrame(data=individuo, columns=[r])
					if len(individuosmovidos)==0:
						individuosmovidos.append(tabla)
					else:
						union=Union(individuosmovidos[0], tabla)
						individuosmovidos[0]=union
		#print "columnas a moverse"
		#print columnas_a_moverse
		#print "estudiantes movidos"
		#print estudiantesmovidos
		if len(row)==len(columnas_a_moverse):
			comunidades_a_eliminarse.append(c)
		else:
			for y in columnas_a_moverse:
				#print comunidades[c]
				comunidades[c].pop(y)
			patron=calcularPatron(comunidades[c])
			patrones[c]=patron
		c+=1
	#print estudiantesmovidos--------tabla=pd.DataFrame(data=estudiante, columns=[r])
	#print data-------comunidades[c].pop(r)
	#print comunidades[1], patrones[1]
	#print comunidades_a_eliminarse, comunidades[0]------comunidades.pop(primer)

	##borro las comunidades en las cuales todos sus estudiantes están mal ubicados
	posiciones_ordenadas=sorted(comunidades_a_eliminarse)
	c=0
	for y in posiciones_ordenadas:
		comunidades.pop(y-c)
		patrones.pop(y-c)
		c+=1
	#print comunidades, patrones
	#print estudiantesmovidos

	retornar.append(individuosmovidos)
	retornar.append(comunidades)
	retornar.append(patrones)
	return retornar

#REAJUSTA LAS COMUNIDADES ENTRANTES
def reajustarComunidades(data, k1, k2, umbral1, umbral2):
	retornar=[]
	#ordenar las comunidades entrantes en una lista
	ordenar=ordenarListaComunidadesEntrantes(data)
	comunidadesEntrantesIniciales=ordenar[0]
	comunidades=ordenar[1]
	patrones=ordenar[2]

	##verificar si cada estudiante pertenece a cada comunidad
	##Y muevo los estudiantes que no pertenecen a la comunidad
	recolectar=recolectarIndividuo(comunidades, patrones, k1, umbral1)
	individuosmovidos=recolectar[0]
	comunidades=[]
	patrones=[]
	comunidades=recolectar[1]
	patrones=recolectar[2]
	
	##a cada estudiante movido se lo compara con los patrones de las comunidades 
	##resultantes para saber si se los asigna a alguna comunidad o se crea una
	if len(individuosmovidos)!=0:
		depositos=depositarIndividuo(individuosmovidos, comunidades, patrones, umbral2, k2)
		comunidades=[]
		patrones=[]
		comunidades=depositos[0]
		patrones=depositos[1]

	retornar.append(comunidades)
	retornar.append(patrones)
	retornar.append(comunidadesEntrantesIniciales)
	return retornar


##GUARDA LAS COMUNIDADES DE UNA COMBINACIÓN ESPECÍFICA
##EN LA BASE DE DATOS
def Guardar_comunidades(comunidades, idc):
	for comunidad in comunidades:
		comunidad.to_csv('static/csv/comunidad.csv', index=False)
		archivo=open('static/csv/comunidad.csv', 'r')
		contenido = archivo.read()
		archivo.close()
		f=ComunidadesFinales(comunidad=contenido, 
			combinaciones_idcombinaciones=Combinaciones.objects.get(idcombinaciones=idc))
		f.save()

##RECUPERO LAS COMUNIDADES FINALES DESDE LA BASE PARA 
##UNA DATA ESPECÍFICA
def Recuperar_comunidades_base(idd):
	consulta=(Combinaciones.objects.filter(data_iddata=idd,cohesion__gt=0,separacion__gt=0, solucion=0).
		values("idcombinaciones", "k1", "k2", "umbral1", "umbral2"
			, "cohesion", "separacion", "numero_comunidades_finales","data_iddata__nombre",
			"data_iddata__escenario").order_by("cohesion").distinct("cohesion")[:10])
	#print consulta
	consulta1=Data.objects.filter(iddata=idd).values("comunidades_iniciales", "numero_individuos")
	comunidades_iniciales=consulta1[0]["comunidades_iniciales"]
	numero_individuos=consulta1[0]["numero_individuos"]
	#print idd, escenario
	for combinacion in consulta:
		combinacion["comunidades_iniciales"]=comunidades_iniciales
		combinacion["individuos"]=numero_individuos

	return consulta

def Recuperar_comunidades_base_propuesta(idd):
	consulta=(Combinaciones.objects.filter(data_iddata=idd,cohesion__gt=0,separacion__gt=0, solucion=1).
		values("idcombinaciones", "k1", "k2", "umbral1", "umbral2", "cohesion", "separacion",
		 "numero_comunidades_finales").order_by("cohesion").distinct("cohesion")[:10])

	consulta1=Data.objects.filter(iddata=idd).values("comunidades_iniciales", "numero_individuos")
	comunidades_iniciales=consulta1[0]["comunidades_iniciales"]
	numero_individuos=consulta1[0]["numero_individuos"]
	#print idd, escenario
	for combinacion in consulta:
		combinacion["comunidades_iniciales"]=comunidades_iniciales
		combinacion["individuos"]=numero_individuos

	return consulta

def recuperar(request, iddata, opsion):
	iddata=int(iddata)
	opsion=int(opsion)
	if opsion==1:
		Inicio(iddata, opsion)
	lista=Recuperar_comunidades_base(iddata)
	idCombinacion=lista[0]["idcombinaciones"]
	nombre_data=lista[0]["data_iddata__nombre"]
	escenario=lista[0]["data_iddata__escenario"]
	lista_seudonimos=Graficar_Circulos(idCombinacion)
	graficarArbol(idCombinacion)
	formulario=False
	opsion=2
	propuesta=False
	return render(request, 'resultado.html', {'lista': lista, 'k1': lista[0]["k1"], 
		'k2': lista[0]["k2"], 'umbral1': lista[0]["umbral1"], 'umbral2': lista[0]["umbral2"], 
		'lista_seudonimos': lista_seudonimos, 'iddata': iddata, 'opsion': opsion,
		'cohesion': lista[0]["cohesion"], 'separacion': lista[0]["separacion"],
		'formulario': formulario, 'idCombinacion': idCombinacion, 'nombre_data': nombre_data,
		'escenario': escenario, 'propuesta': propuesta})

def recuperar_propuesta(request, iddata, opsion):
	iddata=int(iddata)
	opsion=int(opsion)
	#print opsion
	consulta=Combinaciones.objects.filter(data_iddata=iddata, solucion=1).count()
	if consulta==0:
		Inicio(iddata, opsion)
	lista_propuesta=Recuperar_comunidades_base_propuesta(iddata)
	lista=Recuperar_comunidades_base(iddata)
	idCombinacion=lista[0]["idcombinaciones"]
	nombre_data=lista[0]["data_iddata__nombre"]
	escenario=lista[0]["data_iddata__escenario"]
	lista_seudonimos=Graficar_Circulos(idCombinacion)
	graficarArbol(idCombinacion)
	formulario=False
	opsion=2
	propuesta=True
	return render(request, 'resultado.html', {'lista': lista, 'k1': lista[0]["k1"], 
		'k2': lista[0]["k2"], 'umbral1': lista[0]["umbral1"], 'umbral2': lista[0]["umbral2"], 
		'lista_seudonimos': lista_seudonimos, 'iddata': iddata, 'opsion': opsion,
		'cohesion': lista[0]["cohesion"], 'separacion': lista[0]["separacion"],
		'formulario': formulario, 'idCombinacion': idCombinacion, 'nombre_data': nombre_data,
		'escenario': escenario, 'lista_propuesta': lista_propuesta, 'propuesta': propuesta})

def mensaje(request, iddata, opsion):
	iddata=int(iddata)
	opsion=int(opsion)
	return render(request, 'mensaje.html', {'iddata': iddata, 'opsion': opsion})

def mensaje_propuesta(request, iddata):
	iddata=int(iddata)
	opsion=3
	return render(request, 'mensaje.html', {'iddata': iddata, 'opsion': opsion})

def select(request):
	if request.method == 'POST':
        # create a form instance and populate it with data from the request:
		form = form_select(request.POST)
        # check whether it's valid:
		if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL (opcional)
			id_data = request.POST['iddata']
			iddata=int(id_data)
			lista=Recuperar_comunidades_base(iddata)
			idCombinacion=lista[0]["idcombinaciones"]
			nombre_data=lista[0]["data_iddata__nombre"]
			escenario=lista[0]["data_iddata__escenario"]
			lista_seudonimos=Graficar_Circulos(idCombinacion)
			graficarArbol(idCombinacion)
			formulario=False
			opsion=2
			propuesta=False
			return render(request, 'resultado.html', {'lista': lista, 'k1': lista[0]["k1"], 
				'k2': lista[0]["k2"], 'umbral1': lista[0]["umbral1"], 'umbral2': lista[0]["umbral2"], 
				'lista_seudonimos': lista_seudonimos, 'iddata': iddata, 'opsion': opsion,
				'cohesion': lista[0]["cohesion"], 'separacion': lista[0]["separacion"],
				'formulario': formulario, 'idCombinacion': idCombinacion, 
				'nombre_data':nombre_data,'escenario':escenario, 'propuesta': propuesta})
    # if a GET (or any other method) we'll create a blank form
	else:
		form = form_select()
		form1 = forEscenario1()
		form2 = forEscenario2()
		return render(request, 'index.html', {'form1': form1, 'form2': form2, 'form': form})

def graficarArbol(idCombinacion):
	consulta=ComunidadesFinales.objects.filter(combinaciones_idcombinaciones=idCombinacion).values("comunidad")
	comunidades=[]
	for comunidad in consulta:
		contenido = comunidad['comunidad']
		fichero=open("static/csv/comunidad.csv","w")
		fichero.write(contenido)
		fichero.close()
		comunidad_tabla = pd.read_table('static/csv/comunidad.csv', engine='python', sep=',')
		comunidades.append(comunidad_tabla)
	f=open("static/csv/flare.csv","w")
	f.write("id,value\n")
	f.write("Comunidades,\n")
	cont=1
	for comunidad in comunidades:
		f.write("Comunidades.comunidad"+str(cont)+",\n")
		row=list(comunidad.columns.values)
		for individuo in row:
			f.write("Comunidades.comunidad"+str(cont)+"."+str(individuo)+",100\n")
		cont+=1
	f.close()

def Graficar_Circulos(idCombinacion):
	#print idCombinacion
	consulta=ComunidadesFinales.objects.filter(combinaciones_idcombinaciones=idCombinacion).values("comunidad")
	#print len(consulta)
	comunidades=[]
	for comunidad in consulta:
		contenido = comunidad['comunidad']
		fichero=open("static/csv/comunidad.csv","w")
		fichero.write(contenido)
		fichero.close()
		comunidad_tabla = pd.read_table('static/csv/comunidad.csv', engine='python', sep=',')
		comunidades.append(comunidad_tabla)
	#comunidades=set(comunidades)
	#print comunidades
	##escribo las comunidades creadas en el archivo datos.json
	##para visualizarlas
	lista_seudonimos=[]
	f=open("static/json/datos.json","w")
	f.write("{\n")
	f.write('"name": "comunidades",\n')
	f.write('"children": [\n')
	c=0
	contador=0
	for y in comunidades:
		f.write('{\n')
		f.write('"name": "comunidad'+str(c)+'",\n')
		f.write('"children": [\n')
		row=list(y.columns.values)
		cont=0
		for t in row:
			d={}
			if cont!=len(row)-1:
				f.write('{"name": "I'+str(contador)+'", "size": 800},\n')
			else:
				f.write('{"name": "I'+str(contador)+'", "size": 800}\n')
			d['seudonimo']='I'+str(contador)
			d['individuo']=t
			#print d
			lista_seudonimos.append(d)
			contador+=1
			cont+=1
		f.write("]\n")
		if c!=len(comunidades)-1:
			f.write('},\n')
		else:
			f.write('}\n')
		c+=1
	f.write("]\n")
	f.write("}\n")
	f.close()
	#print contador
	return lista_seudonimos

@csrf_exempt
def comunidadesCombinacion(request):
	if request.is_ajax() == True:
		req = {}
		id_combinacion = request.POST.getlist('id_combinacion')
		id_combinacion=int(id_combinacion[0])
		#print id_combinacion
		lista_seudonimos=Graficar_Circulos(id_combinacion)
		graficarArbol(id_combinacion)
		#print lista_seudonimos
		consulta=Combinaciones.objects.filter(idcombinaciones=id_combinacion).all()
		consulta2 = json.dumps( [{'k1': o.k1, 'k2': o.k2, 'umbral1': o.umbral1, 'umbral2': o.umbral2, 'cohesion': o.cohesion, 'separacion': o.separacion} for o in consulta] )
		lista_seudonimos1 = json.dumps( lista_seudonimos )
		req['seudonimo'] = lista_seudonimos1
        req['consulta'] = consulta2
        #req['id_combinacion'] = id_combinacion
        #print consulta2
	return JsonResponse(req, safe=False)

def ejecutar_combinacion(request, iddata):
	iddata=int(iddata)
	#print iddata
	#print seccion
	if request.method == 'POST':
		k1 = request.POST['k1']
		k2 = request.POST['k2']
		umbral1 = request.POST['umbral1']
		umbral2 = request.POST['umbral2']
		#print k1, k2, umbral1, umbral2
		k1=float(k1)
		k2=float(k2)
		umbral1=float(umbral1)
		umbral2=float(umbral2)
		#print lista_seudonimos
		consulta1=Data.objects.filter(iddata=iddata).values("escenario", "data", "numero_individuos")
		#print consulta1
		escenario=consulta1[0]["escenario"]
		contenido=consulta1[0]["data"]
		n_individuos=consulta1[0]["numero_individuos"]
		data=limpiar_contenido(contenido, escenario)
		if escenario==1:
			consulta2=Combinaciones.objects.filter(k2=k2, umbral2=umbral2, 
				data_iddata=iddata).values("idcombinaciones", 'cohesion', 'separacion', 'k1'
				,'umbral1')
			if len(consulta2)==0:
				Escenario1(umbral2, k2, data, iddata, n_individuos, 2)
				Escenario1(umbral2, k2, data, iddata, n_individuos, 3)
				consulta3=Combinaciones.objects.filter(k2=k2, umbral2=umbral2, 
					data_iddata=iddata).values("idcombinaciones", 'cohesion', 'separacion', 
					'k1','umbral1')
				cohesion=consulta3[0]["cohesion"]
				separacion=consulta3[0]["separacion"]
				k1=consulta3[0]["k1"]
				umbral1=consulta3[0]["umbral1"]
				idcombinaciones=consulta3[0]["idcombinaciones"]
			else:
				idcombinaciones=consulta2[0]["idcombinaciones"]
				cohesion=consulta2[0]["cohesion"]
				separacion=consulta2[0]["separacion"]
				k1=consulta2[0]["k1"]
				umbral1=consulta2[0]["umbral1"]
			lista_seudonimos=Graficar_Circulos(idcombinaciones)
			graficarArbol(idcombinaciones)
			lista=Recuperar_comunidades_base(iddata)
			nombre_data=lista[0]["data_iddata__nombre"]
			escenario=lista[0]["data_iddata__escenario"]
		else:
			consulta2=Combinaciones.objects.filter(k2=k2, k1=k1, umbral1=umbral1, 
					umbral2=umbral2, data_iddata=iddata).values("idcombinaciones", 'cohesion', 
					'separacion')
			if len(consulta2)==0:
				Escenario2(umbral2, umbral1, k2, k1, data, iddata, n_individuos, 2)
				Escenario2(umbral2, umbral1, k2, k1, data, iddata, n_individuos, 3)
				consulta3=Combinaciones.objects.filter(k2=k2, k1=k1, umbral1=umbral1, 
					umbral2=umbral2, data_iddata=iddata).values("idcombinaciones", 'cohesion', 
					'separacion')
				cohesion=consulta3[0]["cohesion"]
				separacion=consulta3[0]["separacion"]
				idcombinaciones=consulta3[0]["idcombinaciones"]
			else:
				idcombinaciones=consulta2[0]["idcombinaciones"]
				cohesion=consulta2[0]["cohesion"]
				separacion=consulta2[0]["separacion"]
			lista_seudonimos=Graficar_Circulos(idcombinaciones)
			graficarArbol(idcombinaciones)
			lista=Recuperar_comunidades_base(iddata)
			nombre_data=lista[0]["data_iddata__nombre"]
			escenario=lista[0]["data_iddata__escenario"]
	formulario=True
	idCombinacion=idcombinaciones
	opsion=2
	propuesta=False
	return render(request, 'resultado.html', {'lista': lista, 'k1': k1, 'k2': k2, 
		'umbral1': umbral1, 'umbral2': umbral2, 'lista_seudonimos': lista_seudonimos, 
		'iddata': iddata,'cohesion': cohesion,'separacion': separacion, 'opsion': opsion,
		'formulario':formulario,'idCombinacion': idCombinacion,'nombre_data': nombre_data,
		'escenario': escenario, 'propuesta': propuesta})

def limpiar_contenido(contenido, escenario):
	f=open("static/csv/comunidad.csv","w")
	f.write(contenido)
	f.close()
	data_tabla = pd.read_table('static/csv/comunidad.csv', engine='python', sep=',')
	if escenario==1:
		row=list(data_tabla.columns.values)
		columna_0=list(data_tabla.loc[:,row[0]])
		caracteres=[]
		for fila in columna_0:
			if type(fila)==str:
				caracteres.append(fila)
		if len(columna_0)==len(caracteres):
			data_tabla.pop(row[0])
			return data_tabla
		else:
			return data_tabla

	if escenario==2:
		row=list(data_tabla.columns.values)
		columna_0=list(data_tabla.loc[:,row[0]])
		ceros_o_unos=[]
		caracteres=[]
		for fila in columna_0:
			if (fila==0 or fila==1) or (fila=="0" or fila=="1"):
				ceros_o_unos.append(fila)
			if type(fila)==str:
				caracteres.append(fila)

		if len(columna_0)-1==len(caracteres):
			data_tabla.pop(row[0])
			return data_tabla
		else:
			return data_tabla

def reporte_pdf(request, idCombinacion):
	idcombinaciones=int(idCombinacion)
	numero=Combinaciones.objects.filter(idcombinaciones=idcombinaciones
		).values("data_iddata__numero_individuos", "data_iddata__nombre",
		"k1", "k2", "umbral1", "umbral2")
	k1=numero[0]["k1"]
	k2=numero[0]["k2"]
	umbral1=numero[0]["umbral1"]
	umbral2=numero[0]["umbral2"]
	numero_individuos=numero[0]["data_iddata__numero_individuos"]
	nombre=numero[0]["data_iddata__nombre"]
	consulta=ComunidadesFinales.objects.filter(combinaciones_idcombinaciones=idcombinaciones
		).values("comunidad")
	comunidades_individuos=[]
	for comunidad in consulta:
		contenido = comunidad['comunidad']
		fichero=open("static/csv/comunidad.csv","w")
		fichero.write(contenido)
		fichero.close()
		comunidad_tabla = pd.read_table('static/csv/comunidad.csv', engine='python', sep=',')
		row=list(comunidad_tabla.columns.values)
		comunidades_individuos.append(row)
	#print comunidades_individuos
	fecha=time.strftime("%d/%m/%y")
	#Story = []
	#print fecha
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=comunidades.pdf'
	#doc=SimpleDocTemplate(response,pagesize=A4,rightMargin=72,leftMargin=72,topMargin=2,
	#	bottomMargin=18,)
	# Create the PDF object, using the response object as its "file."
	#buffer=BytesIO()
	temp = StringIO()
	tamanio=len(comunidades_individuos)
	p = canvas.Canvas(temp, pagesize=A4)
	if ((tamanio>2 and numero_individuos<600) or (tamanio<=2 and numero_individuos<600)) or (tamanio>2 and numero_individuos>600):
		p.setLineWidth(.3)
		p.setFont('Helvetica',22)
		p.drawString(30,750,'Agrupar')
		p.setFont('Helvetica',12)
		p.drawString(30,735,'Report; '+nombre+'; '+str(numero_individuos)+' individuos')
		p.setFont('Helvetica',12)
		p.drawString(30,720,
			'K1 = '+str(k1)+'; K2 = '+str(k2)+'; Umbral1 = '+str(umbral1)+
			'; Umbral2 = '+str(umbral2))
		p.setFont('Helvetica-Bold',12)
		p.drawString(480,750,fecha)
		p.line(460,747,560,747)
	#Story.append(p)
	styles=getSampleStyleSheet()
	styleBH=styles["Normal"]
	styleBH.alignment=TA_CENTER
	styleBH.fontSize=10
	comunidad=Paragraph('''COMUNIDAD''',styleBH)
	individuos=Paragraph('''INDIVIDUOS''',styleBH)
	individuosT=Paragraph('''TOTAL INDIVIDUOS''',styleBH)
	data=[]
	data.append([comunidad,individuos,individuosT])
	styles=getSampleStyleSheet()
	styleN=styles["BodyText"]
	styleN.alignment=TA_CENTER
	styleN.fontSize=7
	high=650
	cont=1
	if (tamanio<=2) and (numero_individuos>300):
		high=50
	else:
		if (tamanio<=2) and (numero_individuos>50 and numero_individuos<300):
			high=350
		else:
			high=650
	for comu in comunidades_individuos:
		individuos=''
		ultimo=len(comu)-1
		co=0
		for c in comu:
			if co!=ultimo:
				individuos=individuos+str(c)+'; '
			else:
				individuos=individuos+str(c)
			co+=1
		individuos=Paragraph(individuos,styleN)
		lista=['Comunidad'+str(cont),individuos,str(len(comu))]
		data.append(lista)
		cont+=1
		high=high-18
		if high<30:
			width, height=A4
			table=Table(data,colWidths=[3 * cm, 12 * cm, 4 * cm])
			table.setStyle(TableStyle([
				('INNERGRID',(0,0),(-1,-1),0.25,colors.black),
				('BOX',(0,0),(-1,-1),0.25,colors.black),]))
			table.wrapOn(p,width, height)
			table.drawOn(p,20,high)
			p.showPage() 
			high=841.4
	width, height=A4
	table=Table(data,colWidths=[3 * cm, 12 * cm, 4 * cm])
	table.setStyle(TableStyle([
		('INNERGRID',(0,0),(-1,-1),0.25,colors.black),
		('BOX',(0,0),(-1,-1),0.25,colors.black),]))
	#Story.append(table)
	#if tamanio<=2 and numero_individuos>600:
	#	high=50
	#	p.showPage()
	table.wrapOn(p,width, height)
	table.drawOn(p,20,high)
	#Story.append(table)
	p.showPage()
	p.save()
	#doc.build(Story)
	response.write(temp.getvalue())
	#response.write(Story)
	return response

def ver_grupos_individuos(request, idCombinacion):
	idcombinaciones=int(idCombinacion)
	numero=Combinaciones.objects.filter(idcombinaciones=idcombinaciones
		).values("data_iddata__numero_individuos", "data_iddata__nombre",
		"k1", "k2", "umbral1", "umbral2")
	k1=numero[0]["k1"]
	k2=numero[0]["k2"]
	umbral1=numero[0]["umbral1"]
	umbral2=numero[0]["umbral2"]
	numero_individuos=numero[0]["data_iddata__numero_individuos"]
	nombre=numero[0]["data_iddata__nombre"]
	consulta=ComunidadesFinales.objects.filter(combinaciones_idcombinaciones=idcombinaciones
		).values("comunidad")
	comunidades=[]
	#comunidades1=[]
	cont=1
	for comunidad in consulta:
		grupo=[]
		filas=[]
		contenido = comunidad['comunidad']
		fichero=open("static/csv/comunidad.csv","w")
		fichero.write(contenido)
		fichero.close()
		comunidad_tabla = pd.read_table('static/csv/comunidad.csv', engine='python', sep=',')
		#row=list(comunidad_tabla.columns.values)
		#comunidades1.append(comunidad_tabla)
		row=list(comunidad_tabla.columns.values)
		#diccionario={}
		cnt=0
		for columna in row:
			diccionario={}
			diccionario["individuo"]=columna
			caracteristicas=list(comunidad_tabla.loc[:,columna])
			grupo.append(diccionario)
			#diccionario["caracteristicas"]=caracteristicas
			#columnas.append(caracteristicas)
			if cnt==0:
				for fila in caracteristicas:
					filas.append([fila])
			else:
				contador=0
				for fila in caracteristicas:
					filas[contador].append(fila)
					contador+=1
			cnt+=1
		for fila in filas:
			diccionario={}
			diccionario["caracteristicas"]=fila
			grupo.append(diccionario)
		diccionario={}
		diccionario["n_comunidad"]="Comunidad"+str(cont)
		grupo.append(diccionario)
		cont+=1
		comunidades.append(grupo)
	#for c in comunidades1:
	#	print c
	return render(request, 'ver_agrupaciones.html', {'comunidades': comunidades, 
		'k1': 'k1 = '+str(k1), 'k2': '; k2 = '+str(k2), 'umbral1': '; umbral1 = '+str(umbral1), 
		'umbral2': '; umbral2 = '+str(umbral2), 
		'numero_individuos':'; numero de individuos '+str(numero_individuos),'nombre': nombre})
#consulta=Data.objects.filter(iddata=1).all()
#contenido=consulta[0].data
#f=open("static/csv/comunidad.csv","w")
#f.write(contenido)
#f.close()
#data = pd.read_table('static/csv/comunidad.csv', engine='python', sep=',')
#data1.to_csv('static/csv/comunidad.csv', index=False)