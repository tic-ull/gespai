# coding=utf-8
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from django.shortcuts import render
from django.views import generic
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings as django_settings

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
     return render(request, 'administracion/autorizar_cambio.html')

    if not cambio.requiere_accion_manual:
        """
        Si no se ha intentado ejecutar los scripts de administración
        sobre el cambio se procede a hacerse.
        """
        with StringIO() as out, redirect_stdout(out), redirect_stderr(out):
            if cambio.estado_cambio == "A":
                dar_alta(cambio.becario.email, models.AdministracionEmplazamiento.objects.get(emplazamiento=cambio.plaza.emplazamiento))
            elif cambio.estado_cambio == "R":
                dar_baja(cambio.becario.email, models.AdministracionEmplazamiento.objects.get(emplazamiento=cambio.becario.plaza_asignada.emplazamiento))
            elif cambio.estado_cambio == "T":
                cambiar(cambio.becario.email,
                    models.AdministracionEmplazamiento.objects.get(emplazamiento=cambio.becario.plaza_asignada.emplazamiento),
                    models.AdministracionEmplazamiento.objects.get(emplazamiento=cambio.plaza.emplazamiento))
            logged = out.getvalue()
        cambio.requiere_accion_manual = True
        cambio.save(update_fields=["requiere_accion_manual"])
        return render(request, 'administracion/autorizar_cambio.html', {'cambio': cambio, "log": logged})
    
    if request.POST.get("cambio_final"):
        """
        Si el cambio se hace definitivo se procede a modificar la base
        de datos con el cambio
        """
        becario = cambio.becario
        if cambio.estado_cambio == 'T':
            becario.estado = 'A'
            becario.plaza_asignada = cambio.plaza
        elif cambio.estado_cambio == 'R':
            becario.estado = cambio.estado_cambio
            becario.plaza_asignada = None
            becario.permisos = False
        else:
            becario.estado = cambio.estado_cambio
            becario.plaza_asignada = cambio.plaza
            becario.permisos = True
        try:
            becario.full_clean()
            becario.save()
            # El mes de inicio de la convocatoria es una constante que se declara
            # en el fichero settings.py del proyecto.
            if cambio.fecha_cambio.month < django_settings.MES_INICIO_CONV:
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
            return redirect("cambios:list")
        except ValidationError as e:
            messages.error(request, e.messages[0], extra_tags='alert alert-danger')
            return redirect('cambios:list')
    messages.error(request, "A este cambio ya se le intentaron aplicar los cambios remotos correspondientes. ", extra_tags="alert alert-danger")
    return render(request, 'administracion/autorizar_cambio.html', {'cambio': cambio, "hecho": True})
