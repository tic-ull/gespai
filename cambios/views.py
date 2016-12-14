#coding=utf-8
from django.shortcuts import render
from django.views import generic
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

from gestion import models
from . import forms

# Create your views here.

def group_check(user):
    return user.groups.filter(name__in=['osl', 'tisu']).exists()

@method_decorator(user_passes_test(group_check), name='dispatch')
class ListBecariosView(generic.ListView):
    template_name = 'cambios/list_becarios.html'
    model = models.Becario

@user_passes_test(group_check)
def cambio_becario(request, orden_becario):
    try:
        becario = models.Becario.objects.get(orden=orden_becario)
    except models.Becario.DoesNotExist:
        becario = None

    if request.method == 'POST':
        form = forms.CambioBecarioForm(request.POST, becario=becario)
        if form.is_valid():
            new_cambio_pendiente = models.CambiosPendientes(becario=becario,
            plaza=form.cleaned_data['plaza_cambio'],fecha_cambio=form.cleaned_data['fecha_cambio'],
            estado_cambio=form.cleaned_data['estado_cambio'])
            try:
                new_cambio_pendiente.full_clean()
                new_cambio_pendiente.save()
            except ValidationError as e:
                if e.messages[0].startswith('Cambios pendientes'):
                    messages.error(request, "Ya existe una solicitud de cambio para este becario y esta plaza\
                    para la fecha indicada.", extra_tags='alert alert-danger')
                else:
                    messages.error(request, e.messages[0], extra_tags='alert alert-danger')
                return redirect('cambios:cambio', orden_becario=orden_becario)
            messages.success(request, "Cambio solicitado con éxito", extra_tags='alert alert-success')
            return redirect('cambios:cambio', orden_becario=orden_becario)

    else:
        form = forms.CambioBecarioForm(becario=becario)
    return render(request, 'cambios/cambio_becario.html', {'becario': becario, 'form': form})

def aceptar_cambio(request, id_cambio):
    try:
        cambio = models.CambiosPendientes.objects.get(pk=id_cambio)
    except models.CambiosPendientes.DoesNotExist:
        cambio = None

    if(request.POST.get('aceptar')):
        becario = cambio.becario
        becario.plaza_asignada = cambio.plaza
        if cambio.estado_cambio == 'T':
            becario.estado = 'A'
        else:
            becario.estado = cambio.estado_cambio
        try:
            becario.full_clean()
            becario.save()
            messages.success(request, "Becario modificado con éxito", extra_tags='alert alert-success')
        except ValidationError as e:
            messages.error(request, e.messages[0], extra_tags='alert alert-danger')
    return render(request, 'cambios/aceptar_cambio.html', {'cambio': cambio})
