from django.conf.urls import url

from . import views

app_name = 'administracion'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^autoriza/(?P<pk_cambio>\d+)$', views.autorizar_cambio, name='autorizar')
]
