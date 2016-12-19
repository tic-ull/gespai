from django.conf.urls import url

from . import views

app_name = 'cambios'

urlpatterns = [
    url(r'^$', views.ListBecariosView.as_view(), name='list'),
    url(r'^list/$', views.ListCambiosView.as_view(), name='lista'),
    url(r'^(?P<orden_becario>[0-9]+)/$', views.cambio_becario, name='cambio'),
    url(r'^aceptar/(?P<id_cambio>[0-9]+)/$', views.aceptar_cambio, name='aceptar'),
    url(r'^modificar/(?P<pk>[0-9]+)/$', views.ModificarCambioView.as_view(), name='modificar')
]
