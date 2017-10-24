# -*- encoding: utf-8 -*-
from django.conf.urls import patterns, url

from algoritmo import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^recuperar/(?P<iddata>[0-9]+)/(?P<opsion>[0-9]+)/$', views.recuperar, name='recuperar'),
    url(r'^recuperar_propuesta/(?P<iddata>[0-9]+)/(?P<opsion>[0-9]+)/$', views.recuperar_propuesta, name='recuperar_propuesta'),
    url(r'^mensaje/(?P<iddata>[0-9]+)/(?P<opsion>[0-9]+)/$', views.mensaje, name='mensaje'),
    url(r'^mensaje_propuesta/(?P<iddata>[0-9]+)/$', views.mensaje_propuesta, name='mensaje_propuesta'),
    #url(r'^reenviar/(?P<iddata>[0-9]+)/$', views.reenviar, name='reenviar'),
    url(r'^comunidadesCombinacion$', views.comunidadesCombinacion, name='comunidadesCombinacion'),
    url(r'^ejecutar_combinacion/(?P<iddata>[0-9]+)/$', views.ejecutar_combinacion, name='ejecutar_combinacion'),
    url(r'^select$', views.select, name='select'),
    url(r'^reporte_pdf/(?P<idCombinacion>[0-9]+)/$', views.reporte_pdf, name='reporte_pdf'),
    url(r'^ver_grupos_individuos/(?P<idCombinacion>[0-9]+)/$', views.ver_grupos_individuos, name='ver_grupos_individuos'),
)