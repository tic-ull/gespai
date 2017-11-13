# coding=utf-8

import csv
from io import TextIOWrapper
import re

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext as _

from gestion import models
from gespai.validation import is_dni

def import_csv_becarios(csv_file):
    csvf = TextIOWrapper(csv_file, encoding="utf-8")
    reader = csv.reader(csvf)
    errors = []

    for index, row in enumerate(reader):
            nueva_titulacion, titulacion_existe = models.Titulacion.objects.get_or_create(codigo=row[10], nombre=row[11])
            if not titulacion_existe:
                nueva_titulacion.full_clean()
                nueva_titulacion.save()

            nuevo_becario = models.Becario(orden=row[1],
                                         estado=row[2][0],
                                         dni=row[3],
                                         apellido1=row[4],
                                         apellido2=row[5],
                                         nombre=row[6],
                                         email=row[7],
                                         telefono=row[8] or None,
                                         titulacion=nueva_titulacion,
                                         permisos=has_permisos(row[9]))
            try:
                nuevo_becario.full_clean()
                nuevo_becario.save()
            except ValidationError as e:
                errors.append((index + 1, e))

    return errors


def import_csv_emplazamientos_plazas(csv_file):
    csvf = TextIOWrapper(csv_file, encoding="utf-8")
    reader = csv.reader(csvf)
    errors = []

    for index, row in enumerate(reader):

        # XXX Hay que ignorar la primera línea para no causar problemas
        if index == 0: continue

        nombre = find_nombre(reader, index)

        # NOTE El siguiente comentario es plenamente falso, get_or_create devuelve un
        # tupla de la forma (objeto_creado, bool_si_existe), lo único que hay que hacer
        # es validar el objeto creado si no existía previamente y guardarlo.

        # Se comprueba si existe ya un Emplazamiento con el mismo nombre. Si no existe,
        # se crea. No se utiliza get_or_create ya que es necesario hacer validación
        # de los campos mediante full_clean.
        try:
            new_emplazamiento = models.Emplazamiento.objects.get(nombre=nombre)
        except ObjectDoesNotExist:
            new_emplazamiento = models.Emplazamiento(nombre=nombre)

        try:
            new_emplazamiento.full_clean()
            new_emplazamiento.save()
        except ValidationError as e:
            errors.append("Error en linea " + (index + 1) + ": " + e.error_dict)
        new_plaza = models.Plaza(pk=row[0], horario=row[1], emplazamiento=new_emplazamiento)

        try:
            new_plaza.full_clean()
            new_plaza.save()
        except ValidationError as e:
            errors.append((index + 1, e))

        if is_dni(row[6]):
            # De nuevo se omite usar get_or_create ya que hay que hacer
            # validación
            try:
                becario = models.Becario.objects.get(dni=row[6])
                becario.plaza_asignada = new_plaza
                becario.save()
            except ObjectDoesNotExist:
                if is_codigo_tit(row[14]):
                    try:
                        new_titulacion = models.Titulacion.objects.get(codigo=row[14])
                    except ObjectDoesNotExist:
                        new_titulacion = models.Titulacion(codigo=row[14], nombre='Titulación desconocida')
                        new_titulacion.save()
                becario = models.Becario(orden=row[5],
                                         dni=row[6],
                                         apellido1=row[7],
                                         apellido2=row[8],
                                         nombre=row[9],
                                         email=row[11],
                                         telefono=row[12] or None,
                                         permisos=has_permisos(row[13]),
                                         titulacion=new_titulacion)
                try:
                    # Se asigna la plaza tras la creación del objeto para que se disparen
                    # las verificaciones del método save()
                    becario.plaza_asignada = new_plaza
                    becario.full_clean()
                    becario.save()
                except ValidationError as e:
                    errors.append((index + 1, e))

    return errors

def import_csv_plan_formacion(csv_file):
    csvf = TextIOWrapper(csv_file, encoding="utf-8")
    reader = csv.reader(csvf)
    errors = []

    # Se recorre todo el fichero CSV para crear los cursos
    for index, row in enumerate(reader):
        if is_codigo_actividad(row[1]):
            try:
                # Se busca la fecha de impartición del curso
                match = re.search('(\d{2})/(\d{2})/(\d{4})', row[2])
                # Se elimina la fecha para quedarnos solo con el nombre
                nombre = re.sub('\(\d{2}/\d{2}/\d{4}\)', '', row[2])
                dia = match.group(1)
                mes = match.group(2)
                anyo = match.group(3)
                # Se forma una fecha apta para el campo DateTimeField
                fecha = anyo + '-' + mes + '-' + dia
                # Se crea un objeto PlanFormacion
                new_plan_formacion = models.PlanFormacion(codigo=row[1], nombre_curso=nombre,
                fecha_imparticion=fecha)
            except AttributeError:
                # Si no se encuentra una fecha en el nombre, se crea un curso sin fecha
                new_plan_formacion = models.PlanFormacion(codigo=row[1], nombre_curso=row[2])

            try:
                new_plan_formacion.full_clean()
                new_plan_formacion.save()
            except ValidationError as e:
                errors.append((index + 1, e))

    # Una vez creados los cursos se comprueba qué becarios han asistido
    for index, row in enumerate(reader):
        if is_dni(row[3]):
            try:
                # Se busca el becario antes de entrar al bucle para reducir el número
                # de accesos a la BD
                becario = models.Becario.objects.get(dni=row[3])
                # Necesito saber el índice de la columna del CSV en la que me encuentro
                # para poder buscar el código de curso asociado a esa columna en la primera línea
                for ind, item in enumerate(row):
                    # Se busca el código del curso en la primera línea del CSV
                    if is_codigo_actividad(reader[0][ind]):
                        curso = models.PlanFormacion.objects.get(codigo=reader[0][ind])
                        new_asistencia = models.AsistenciaFormacion(becario=becario, curso=curso)
                        try:
                            # Si el becario ha asistido
                            if item == 'Sí':
                                new_asistencia.asistencia = True
                            new_asistencia.full_clean()
                            new_asistencia.save()
                        except ValidationError as e:
                            errors.append((index + 1, e))
            except ObjectDoesNotExist as e:
                errors.append((index + 1, e))

    raise ValidationError(errors)
    return errors


# Método recursivo para encontrar el nombre de Emplazamiento en campos vacíos (porque
# los nombres repetidos aparecen como campos vacíos en el CSV)
def find_nombre(rows, ind):
    if rows[ind][2]:
        return rows[ind][2]
    else:
        return find_nombre(rows, (ind - 1))

# Métodos para comprobar si los campos del CSV son válidos

def is_codigo_tit(cod):
    return len(cod) == 4 and cod[0].isalpha() and cod[1:].isdigit()

def has_permisos(perm):
    return perm == "Sí"

def is_codigo_actividad(cod):
    return len(cod) > 0 and len(cod) <= 3 and cod[0] == 'A'
