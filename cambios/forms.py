from django import forms

from gestion import models


class CambioBecarioForm(forms.Form):
    plazas = models.Plaza.objects.all()
    plazas_libres_pks = []
    for plaza in plazas:
        if not plaza.becario_set.all():
            plazas_libres_pks.append(plaza.pk)

    plazas_libres = models.Plaza.objects.filter(pk__in=plazas_libres_pks)

    ESTADOS = (
        ('A', 'Asignado'),
        ('R', 'Renuncia'),
        ('T', 'Traslado'),
    )

    plaza_cambio = forms.ModelChoiceField(queryset=plazas_libres)
    # TODO: Si es estado_cambio = 'Traslado', plaza_cambio no debe ser null
    estado_cambio = forms.ChoiceField(choices=ESTADOS)
    formatos_fecha = ['%d-%m-%Y',
                      '%d-%m-%y',
                      '%d/%m/%Y',
                      '%d/%m/%y']
    fecha_cambio = forms.DateField(input_formats=formatos_fecha, widget=forms.SelectDateWidget)
