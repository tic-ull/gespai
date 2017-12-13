# coding=utf-8
from io import StringIO
from contextlib import redirect_stdout

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

from gespai.administracion import *

def group_check_osl(user):
    return user.groups.filter(name='osl').exists()

@method_decorator(user_passes_test(group_check_osl), name='dispatch')
class IndexView(generic.TemplateView):
    template_name = 'administracion/index.html'


@user_passes_test(group_check_osl)
def autorizar_cambio(request, pk_cambio):
    try:
        cambio = models.CambiosPendientes.objects.get(pk=pk_cambio)
    except models.CambiosPendientes.DoesNotExist:
        cambio = None

    if request.method == 'POST':
        if 'cambio' in request.POST:
            with StringIO() as out, redirect_stdout(out):
                dar_alta("alu0100791327", "biologia")
                logged = out.getvalue()
        return render(request, 'administracion/autorizar_cambio.html', {'cambio': cambio, "log": logged})
            
    return render(request, 'administracion/autorizar_cambio.html', {'cambio': cambio})
