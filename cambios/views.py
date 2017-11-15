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
    return user.groups.filter(name__in=['osl', 'tisu', "vicerrectorado"]).exists()


def group_check_osl(user):
    return user.groups.filter(name='osl').exists()


@method_decorator(user_passes_test(group_check_all), name='dispatch')
class IndexView(generic.TemplateView):
    template_name = 'cambios/index.html'


@method_decorator(user_passes_test(group_check_all), name='dispatch')
class ListBecariosView(generic.ListView):
    template_name = 'cambios/list_becarios.html'
    model = models.Becario


@user_passes_test(group_check_all)
def cambio_becario(request, orden_becario):
    try:
        becario = models.Becario.objects.get(orden=orden_becario)
    except models.Becario.DoesNotExist:
        becario = None

    if request.method == 'POST':
        if 'cambio' in request.POST:
            form_cambio = forms.CambioBecarioForm(
                request.POST, becario=becario, prefix='cambio')
            if form_cambio.is_valid():
                new_cambio_pendiente = models.CambiosPendientes(becario=becario,plaza=form_cambio.cleaned_data['plaza'],
                    fecha_cambio=form_cambio.cleaned_data['fecha_cambio'],
                    estado_cambio=form_cambio.cleaned_data['estado_cambio'],
                    observaciones=form_cambio.cleaned_data['observaciones'])
                if new_cambio_pendiente.estado_cambio == 'R':
                    new_cambio_pendiente.plaza = None
                try:
                    new_cambio_pendiente.full_clean()
                    new_cambio_pendiente.save()
                except ValidationError as e:
                    if e.messages[0].startswith('Cambios pendientes'):
                        messages.error(request, "Ya existe una solicitud de cambio para este becario y esta plaza\
                        para la fecha indicada.", extra_tags='alert alert-danger')
                    else:
                        messages.error(request, e.messages[
                                       0], extra_tags='alert alert-danger')
                    return redirect('cambios:cambio', orden_becario=orden_becario)
                messages.success(
                    request, "Cambio solicitado con éxito", extra_tags='alert alert-success')
                return redirect('cambios:cambio', orden_becario=orden_becario)
            form_obs = forms.ObservacionesBecarioForm(
                becario=becario, prefix='obs')
        elif 'observaciones' in request.POST:
            form_obs = forms.ObservacionesBecarioForm(
                request.POST, becario=becario, prefix='obs')
            if form_obs.is_valid():
                becario.observaciones = form_obs.cleaned_data['observaciones']
                try:
                    becario.full_clean()
                    becario.save()
                except ValidationError as e:
                    messages.error(request, messages[
                                   0], extra_tags='alert alert-danger')
                    return redirect('cambios:cambio', orden_becario=orden_becario)
                messages.success(
                    request, "Observaciones modificadas con éxito", extra_tags='alert alert-success')
                return redirect('cambios:cambio', orden_becario=orden_becario)

            form_cambio = forms.CambioBecarioForm(
                becario=becario, prefix='cambio')

    else:
        form_cambio = forms.CambioBecarioForm(becario=becario, prefix='cambio')
        form_obs = forms.ObservacionesBecarioForm(
            becario=becario, prefix='obs')
    return render(request, 'cambios/cambio_becario.html', {'becario': becario,
                                                           'form_cambio': form_cambio,
                                                           'form_obs': form_obs})


@user_passes_test(group_check_osl)
def aceptar_cambio(request, id_cambio):
    try:
        cambio = models.CambiosPendientes.objects.get(pk=id_cambio)
    except models.CambiosPendientes.DoesNotExist:
        cambio = None

    if(request.POST.get('aceptar') and cambio):
        becario = cambio.becario
        becario.plaza_asignada = cambio.plaza
        if cambio.estado_cambio == 'T':
            becario.estado = 'A'
        elif cambio.estado_cambio == 'R':
            becario.estado = cambio.estado_cambio
            becario.plaza_asignada = None
        else:
            becario.estado = cambio.estado_cambio
        try:
            becario.full_clean()
            becario.save()
            # El mes de inicio de la convocatoria es una constante que se declara
            # en el fichero settings.py del proyecto.
            if cambio.fecha_cambio.month < settings.MES_INICIO_CONV:
                conv, c = models.Convocatoria.objects.get_or_create(anyo_inicio=cambio.fecha_cambio.year - 1,
                                                                    anyo_fin=cambio.fecha_cambio.year)
            else:
                conv, c = models.Convocatoria.objects.get_or_create(anyo_inicio=cambio.fecha_cambio.year,
                                                                    anyo_fin=cambio.fecha_cambio.year + 1)
            hist, c = models.HistorialBecarios.objects.get_or_create(dni_becario=becario.dni,
                                                            convocatoria=conv)
            if cambio.estado_cambio == 'A':
                hist.fecha_asignacion = cambio.fecha_cambio
            elif cambio.estado_cambio == 'R':
                hist.fecha_renuncia = cambio.fecha_cambio
            hist.full_clean()
            hist.save()
            cambio.delete()
        except ValidationError as e:
            messages.error(request, e.messages[0], extra_tags='alert alert-danger')
            return redirect('cambios:aceptar', id_cambio=id_cambio)
        return render(request, 'gespai/success.html', {'error': False,
                                                       'mensaje': 'Cambio aplicado con éxito'})
    return render(request, 'cambios/aceptar_cambio.html', {'cambio': cambio})


@method_decorator(user_passes_test(group_check_all), name='dispatch')
class ModificarCambioView(SuccessMessageMixin, generic.UpdateView):
    model = models.CambiosPendientes
    template_name = 'cambios/modificar_cambio.html'
    form_class = forms.CambioBecarioForm
    success_url = '#'
    success_message = "Cambio modificado con éxito"

    def get_form_kwargs(self):
        kwargs = super(ModificarCambioView, self).get_form_kwargs()
        kwargs.update({'becario': self.object.becario})
        return kwargs


@method_decorator(user_passes_test(group_check_all), name='dispatch')
class ListCambiosView(generic.ListView):
    template_name = 'cambios/list_cambios.html'
    model = models.CambiosPendientes
