from django.shortcuts import render
from django.views import generic
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponseRedirect

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
            print(form.cleaned_data)
            new_cambio_pendiente = models.CambiosPendientes(becario=becario,
            plaza=form.cleaned_data['plaza_cambio'],fecha_cambio=form.cleaned_data['fecha_cambio'],
            estado_cambio=form.cleaned_data['estado_cambio'])
            try:
                new_cambio_pendiente.full_clean()
                new_cambio_pendiente.save()
            except ValidationError as e:
                messages.error(request, e.message)
                return HttpResponseRedirect('/cambios/' + orden_becario)
            return HttpResponseRedirect('/cambios')

    else:
        form = forms.CambioBecarioForm(becario=becario)
    return render(request, 'cambios/cambio_becario.html', {'becario': becario, 'form': form})
