# coding=utf-8
import csv
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from gestion import models


def import_csv_becarios(csv_file):
    reader = csv.reader(csv_file)
    errors = []

    for index, row in enumerate(reader):

        new_becario = models.Becario(estado=row[2][:1], dni=row[3], apellido1=row[4].decode('utf-8'),
        apellido2=row[5].decode('utf-8'), nombre=row[6].decode('utf-8'), email=row[7],
        telefono=row[8] or None, titulacion=row[11], permisos=has_permisos(row[9]))
        try:
            new_becario.full_clean()
            new_becario.save()
        except ValidationError as e:
            errors.append("Error en linea " +
                                unicode(index + 1) + ": " + unicode(e.error_dict))
    if errors:
        raise ValidationError(errors)


def import_csv_centros_plazas(csv_file):
    reader = list(csv.reader(csv_file))
    errors = []

    for index, row in enumerate(reader):

        nombre = find_nombre(reader, index)
        print('nombre magico de línea: ' + str(index) + ': ' + str(nombre))
        # Se comprueba si existe ya un Centro con el mismo nombre. Si no existe,
        # se crea. No se utiliza get_or_create ya que es necesario hacer validación
        # de los campos mediante full_clean.
        try:
            new_centro = models.Centro.objects.get(nombre=nombre)
        except ObjectDoesNotExist:
            new_centro = models.Centro(nombre=nombre)
        # sobra? ya compruebo que el nombre no coincida, y Centro solo tiene
        # nombre e id automática
        try:
            new_centro.full_clean()
            new_centro.save()
        except ValidationError as e:
            errors.append("Error en linea " +
                          unicode(index + 1) + ": " + unicode(e.error_dict))
        new_plaza = models.Plaza(pk=row[0], horario=row[1], centro=new_centro)

        try:
            new_plaza.full_clean()
            new_plaza.save()
        except ValidationError as e:
            errors.append("Error en linea " +
                          unicode(index + 1) + ": " + unicode(e.error_dict))

        if is_dni(row[6]):
            # De nuevo se omite usar get_or_create ya que hay que hacer validación
            try:
                becario = models.Becario.objects.get(dni=row[6])
                becario.plaza_asignada = new_plaza
                becario.save()
            except ObjectDoesNotExist:
                becario = models.Becario(dni=row[6], apellido1=row[7].decode('utf-8'),
                apellido2=row[8].decode('utf-8'), nombre=row[9].decode('utf-8'),
                email=row[11], telefono=row[12] or None, permisos=has_permisos(row[13]),
                titulacion=row[14])
                try:
                    # Se asigna la plaza tras la creación del objeto para que se disparen
                    # las verificaciones del método save()
                    becario.plaza_asignada=new_plaza
                    becario.full_clean()
                    becario.save()
                except ValidationError as e:
                    errors.append("Error en linea " +
                                  unicode(index + 1) + ": " + unicode(e.error_dict))

    if errors:
        raise ValidationError(errors)


# Método recursivo para encontrar el nombre de Centro en campos vacíos (porque
# los nombres repetidos aparecen como campos vacíos en el CSV)
def find_nombre(rows, ind):
    if rows[ind][2]:
        return rows[ind][2]
    else:
        return find_nombre(rows, (ind - 1))


def is_dni(dni):
    if len(dni) == 8:
        if (dni[0].isalpha() and dni[1:].isdigit()) or dni.isdigit():
            return True
    return False


def has_permisos(perm):
    if perm == 'Sí':
        return True
    else:
        return False
