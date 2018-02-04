from django.conf.urls import url

from . import views

app_name = 'personal'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^info/$', views.InfoView.as_view(), name='info'),
    url(r'^preferencias/$', views.ListPreferenciasView.as_view(), name='preferencias'),
]
