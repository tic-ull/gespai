from django import forms
import datetime

from gestion import models

class ObservacionesBecarioForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.becario = kwargs.pop('becario')
        super(ObservacionesBecarioForm, self).__init__(*args, **kwargs)
        if self.becario:
            self.fields['observaciones'].initial = self.becario.observaciones

    observaciones = forms.CharField(label="Observaciones",
        widget=forms.Textarea(attrs={'cols':50, 'rows':5, 'class': 'form-control'}))

class CambioBecarioForm(forms.ModelForm):
    class Meta:
        model = models.CambiosPendientes
        exclude = ('becario', "requiere_accion_manual")

    def __init__(self, *args, **kwargs):
        self.becario = kwargs.pop('becario')
        super(CambioBecarioForm, self).__init__(*args, **kwargs)
        if self.becario and self.becario.plaza_asignada:
            self.fields['plaza'].initial = self.becario.plaza_asignada

    ESTADOS = (
        ('A', 'Asignado'),
        ('R', 'Renuncia'),
        ('T', 'Traslado'),
    )

    plaza = forms.ModelChoiceField(
        label="Plaza de cambio", queryset=models.Plaza.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    estado_cambio = forms.ChoiceField(label="Estado de cambio", choices=ESTADOS, widget=forms.Select(attrs={'class': 'form-control'}))
    fecha_cambio = forms.DateField(label="Fecha de cambio", widget=forms.SelectDateWidget(attrs={'class': 'form-control'}),
        initial=datetime.date.today, required=False)
    observaciones = forms.CharField(label="Observaciones del cambio", widget=forms.Textarea(attrs={'cols':50, 'rows':5, 'class': 'form-control'}),
        required=False)

    def clean(self):
        cleaned_data = super(CambioBecarioForm, self).clean()
        estado = cleaned_data.get('estado_cambio')
        plaza = cleaned_data.get('plaza')
        fecha = cleaned_data.get('fecha_cambio')

        if estado == 'T' and not plaza:
            self.add_error('plaza', 'Debe seleccionar una plaza si el cambio es un traslado.')
        if estado == 'T' and plaza == self.becario.plaza_asignada:
            self.add_error('plaza', 'Un becario no puede ser trasladado a su misma plaza.')
        if estado == 'A' and self.becario.estado == 'A':
            self.add_error('estado_cambio', 'Si desea asignar al becario a otra plaza, seleccione Traslado como estado de cambio.')
        if fecha < datetime.date.today():
            self.add_error('fecha_cambio', 'Seleccione una fecha en el futuro.')
