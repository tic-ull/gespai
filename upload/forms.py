from django import forms
from django.core.exceptions import ValidationError

class UploadCSVForm(forms.Form):
    csv_file_field = forms.FileField(label='Seleccione un fichero CSV',
                                     help_text='Se aceptan ficheros CSV que sigan el formato indicado.')

    def clean_csv_file_field(self):
        csv_file = self.cleaned_data.get('csv_file_field')
        if not csv_file.name.endswith('.csv'):
            raise ValidationError(u'Solo se aceptan ficheros CSV')
        return csv_file
