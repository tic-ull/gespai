import csv
from django.core.exceptions import ValidationError

from gestion import models

def import_csv_becarios(csv_file):
    reader = csv.reader(csv_file)
    new_becarios = []
    # pp = pprint.PrettyPrinter(indent=4)
    if new_becarios:
        print("Esto no deberia verse NUNCA")
    for index, row in enumerate(reader):
        if not row[8]:
            row[8] = None
        new_becario = models.Becario(estado=row[2][:1], dni=row[3], apellido1=row[4], apellido2=row[5],
                               nombre=row[6], email=row[7], telefono=row[8], titulacion=row[11])

        try:
            new_becario.full_clean()
            new_becario.save()
        except ValidationError as e:
            print "Error en linea", (index + 1)
            # print e.error_dict[0]
            new_becarios.append("Error en linea " +
                             str(index + 1) + ": " + e.error_dict)
    if new_becarios:
        raise forms.ValidationError(new_becarios)
