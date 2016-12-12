#coding=utf-8
from django.shortcuts import render
from django.views import generic
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponseRedirect
import pdb

from gestion import models
from . import forms

# Create your views here.

class ListBecariosView(generic.ListView):
    template_name = 'cambios/list_becarios.html'
    model = models.Becario

def cambio_becario(request, orden_becario):
    try:
        becario = models.Becario.objects.get(orden=orden_becario)
    except models.Becario.DoesNotExist:
        becario = None

    if request.method == 'POST':
        form = forms.CambioBecarioForm(request.POST, becario=becario)
        if form.is_valid():
            print("El form esta bien")
            new_cambio_pendiente = models.CambiosPendientes(becario=becario,
            plaza=form.cleaned_data['plaza_cambio'],fecha_cambio=form.cleaned_data['fecha_cambio'],
            estado_cambio=form.cleaned_data['estado_cambio'])
            try:
                new_cambio_pendiente.full_clean()
                new_cambio_pendiente.save()
            except ValidationError as e:
                #pdb.set_trace()
                print("error al meter el rollo " + e.message)
                messages.error(request, "Se ha producido un error al almacenar el cambio.\
                O bien está intentando solicitar un cambio ya existente o el becario para\
                el que solicita el cambio ya ha recibido beca en cinco convocatorias")
                return HttpResponseRedirect('/cambios/' + orden_becario)
            return HttpResponseRedirect('/cambios')

    else:
        form = forms.CambioBecarioForm(becario=becario)
    return render(request, 'cambios/cambio_becario.html', {'becario': becario, 'form': form})
