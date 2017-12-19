from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = "responsables"

urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="responsables/index.html"), name='index'),
    url(r"^becarios/$", views.BecariosView.as_view(), name='becarios'),
]
