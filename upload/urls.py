from django.conf.urls import url

from . import views

app_name = 'upload'

urlpatterns = [
    url(r'^$', views.UploadView.as_view(), name='index'),
    url(r'^becarios/$', views.upload_becarios, name='upload_becarios'),
    url(r'^plazas/$', views.upload_centros_plazas, name='upload_plazas'),
    url(r'^formacion/$', views.upload_plan_formacion, name='upload_formacion')
]
