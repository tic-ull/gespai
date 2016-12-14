from django.conf.urls import url

from . import views

app_name = 'cambios'

urlpatterns = [
    url(r'^$', views.ListBecariosView.as_view(), name='list'),
    url(r'^(?P<orden_becario>[0-9]+)/$', views.cambio_becario, name='cambio'),
    url(r'^aceptar/(?P<id_cambio>[0-9]+)/$', views.aceptar_cambio, name='aceptar')
]
