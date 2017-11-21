# coding=utf-8
from django.shortcuts import render
from django.views import generic
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings

from gestion import models
from . import forms

def group_check_all(user):
    return user.groups.filter(name="alu").exists()

@method_decorator(user_passes_test(group_check_all), name='dispatch')
class IndexView(generic.TemplateView):
    template_name = 'personal/index.html'

@method_decorator(user_passes_test(group_check_all), name='dispatch')
class InfoView(generic.ListView):
    template_name = 'personal/info.html'
    queryset = models.Becario.objects.filter(dni="78633820V")

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)
        context["becario"] = models.Becario.objects.get(dni="78633820V")
        return context

# TODO:jeplasenciap:2017-11-20T1140:(#17):
# Conectar las cuentas de los usuarios con su autenticación del CAS
# de tal manera que sólo se muestren las preferencias guardadas del
# usuario/alumno conectado.
@method_decorator(user_passes_test(group_check_all), name='dispatch')
class ListPreferenciasView(generic.ListView):
    template_name = 'personal/list_preferencias.html'
    queryset  = models.PreferenciasBecario.objects.filter(becario_id="78633820V")
    def get_context_data(self, **kwargs):
        context = super(ListPreferenciasView, self).get_context_data(**kwargs)
        #context["preferencias"] = models.PreferenciasBecario.objects.filter(becario_id="1").order_by("orden")
        context["preferencias"] = models.PreferenciasBecario.objects.filter(becario_id="78633820V").order_by("orden")
        return context
