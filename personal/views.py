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

# TODO:2011-11-17T14:13:(#17):jeplasenciap:
# Falta correctamente pasar argumentos a la plantilla y hacer la
# plantilla en sí
@method_decorator(user_passes_test(group_check_all), name='dispatch')
class InfoView(generic.ListView):
    template_name = 'personal/info.html'
    model = models.Becario
    queryset = models.Becario.objects.get(dni="78633820V")

@method_decorator(user_passes_test(group_check_all), name='dispatch')
class ListPreferenciasView(generic.ListView):
    template_name = 'personal/list_preferencias.html'
    model = models.PreferenciasBecario
    queryset = models.PreferenciasBecario.objects.filter(becario_id="23").order_by("orden")
