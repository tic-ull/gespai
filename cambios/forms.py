from django import forms

from gestion import models


class CambioBecarioForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.becario = kwargs.pop('becario')
        super(CambioBecarioForm, self).__init__(*args, **kwargs)
        if self.becario and self.becario.plaza_asignada:
            self.fields['plaza_cambio'].initial = self.becario.plaza_asignada

    ESTADOS = (
        ('A', 'Asignado'),
        ('R', 'Renuncia'),
        ('T', 'Traslado'),
    )

    plaza_cambio = forms.ModelChoiceField(label="Plaza de cambio", queryset=models.Plaza.objects.all())
    estado_cambio = forms.ChoiceField(label="Estado de cambio", choices=ESTADOS)
    fecha_cambio = forms.DateField(label="Fecha de cambio", widget=forms.SelectDateWidget)
