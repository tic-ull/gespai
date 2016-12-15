from django import forms
import datetime

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

    plaza_cambio = forms.ModelChoiceField(
        label="Plaza de cambio", queryset=models.Plaza.objects.all(), required=False)
    estado_cambio = forms.ChoiceField(label="Estado de cambio", choices=ESTADOS)
    fecha_cambio = forms.DateField(label="Fecha de cambio", widget=forms.SelectDateWidget,
        initial=datetime.date.today)

    def clean(self):
        cleaned_data = super(CambioBecarioForm, self).clean()
        estado = cleaned_data.get('estado_cambio')
        plaza = cleaned_data.get('plaza_cambio')
        fecha = cleaned_data.get('fecha_cambio')

        if estado == 'T' and not plaza:
            self.add_error('plaza_cambio', 'Debe seleccionar una plaza si el cambio es un traslado.')
        if estado == 'T' and plaza == self.becario.plaza_asignada:
            self.add_error('plaza_cambio', 'Un becario no puede ser trasladado a su misma plaza.')
        if estado == 'A' and self.becario.estado == 'A':
            self.add_error('estado_cambio', 'Si desea asignar al becario a otra plaza, seleccione Traslado como estado de cambio.')
        if fecha < datetime.date.today():
            self.add_error('fecha_cambio', 'Seleccione una fecha en el futuro.')
