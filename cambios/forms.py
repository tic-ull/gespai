from django import forms

from gestion import models


class CambioBecarioForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.becario = kwargs.pop('becario')
        super(CambioBecarioForm, self).__init__(*args, **kwargs)
        print(unicode(self.becario.email))
        if self.becario.plaza_asignada:
            self.fields['plaza_cambio'].initial = self.becario.plaza_asignada

    ESTADOS = (
        ('A', 'Asignado'),
        ('R', 'Renuncia'),
        ('T', 'Traslado'),
    )

    plaza_cambio = forms.ModelChoiceField(queryset=models.Plaza.objects.all())
    # TODO: Si es estado_cambio = 'Traslado', plaza_cambio no debe ser null
    estado_cambio = forms.ChoiceField(choices=ESTADOS)
    fecha_cambio = forms.DateField(widget=forms.SelectDateWidget)

    #def clean(self):

def get_plazas_libres():
    plazas = models.Plaza.objects.all()
    plazas_libres_pks = []
    for plaza in plazas:
        if not plaza.becario_set.all():
            plazas_libres_pks.append(plaza.pk)

    return models.Plaza.objects.filter(pk__in=plazas_libres_pks)
