from django.shortcuts import render
from django.views import generic

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
        form = forms.CambioBecarioForm(request.POST)
        if form.is_valid():
            print('magia')
    else:
        form = forms.CambioBecarioForm()
    return render(request, 'cambios/cambio_becario.html', {'becario': becario, 'form': form})
