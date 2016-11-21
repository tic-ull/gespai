# coding=utf-8
import csv
from django.core.exceptions import ValidationError

from gestion import models


def import_csv_becarios(csv_file):
    reader = csv.reader(csv_file)
    new_becarios = []

    for index, row in enumerate(reader):
        if not row[8]:
            row[8] = None
        if row[9] == 'Sí':
            bool_permisos = True
        else:
            bool_permisos = False

        new_becario = models.Becario(estado=row[2][:1], dni=row[3], apellido1=row[4], apellido2=row[5],
                                     nombre=row[6], email=row[7], telefono=row[8], titulacion=row[11], permisos=bool_permisos)
        try:
            new_becario.full_clean()
            new_becario.save()
        except ValidationError as e:
            new_becarios.append("Error en linea " +
                                unicode(index + 1) + ": " + unicode(e.error_dict))
    if new_becarios:
        raise ValidationError(new_becarios)
