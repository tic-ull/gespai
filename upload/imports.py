# coding=utf-8

import csv
from io import TextIOWrapper
import re

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext as _

from gestion import models
from gespai.validation import is_dni


bdict = {
    "orden":        1, 
    "estado":       2,
    "dni":          3,
    "apellido1":    4,
    "apellido2":    5,
    "nombre":       6,
    "email":        7,
    "telefono":     8,
    "permisos":     9,
    "codigo_titl": 10,
    "nombre_titl": 11
}
def import_csv_becarios(csv_file):
    csvf = TextIOWrapper(csv_file, encoding="utf-8")
    reader = csv.reader(csvf)
    errors = []

    for index, row in enumerate(reader):
        if index < 3:
            continue
        try:
            nueva_titulacion = models.Titulacion.objects.get(
                codigo=row[bdict["codigo_titl"]],
                nombre=row[bdict["nombre_titl"]])
        except models.Titulacion.DoesNotExist:
            nueva_titulacion = models.Titulacion(
                codigo=row[bdict["codigo_titl"]],
                nombre=row[bdict["nombre_titl"]])
            try:
                nueva_titulacion.full_clean()
                nueva_titulacion.save()
            except ValidationError as e:
                errors.append(ValidationError(
                    _("Error en la línea %(i)s: %(error)s"),
                    params={"i": index+1, "error": e}
                ))

        nuevo_becario = models.Becario(
            orden=row[bdict["orden"]],
            estado=row[bdict["estado"]][0],
            dni=row[bdict["dni"]],
            apellido1=row[bdict["apellido1"]],
            apellido2=row[bdict["apellido2"]],
            nombre=row[bdict["nombre"]],
            email=row[bdict["email"]],
            telefono=row[bdict["telefono"]] or None,
            titulacion=nueva_titulacion,
            permisos=has_permisos(row[bdict["permisos"]])
        )
        try:
            nuevo_becario.full_clean()
            nuevo_becario.save()
        except ValidationError as e:
            errors.append(ValidationError(
                _("Error en la línea %(i)s: %(error)s"),
                params={"i": index+1, "error": e}
            ))

    if errors:
        raise ValidationError(errors)

cdict = {
    "pk":      0, #: El id de la plaza
    "horario": 1,
    "nombre":  2,
    "dni":     6
}
def import_csv_emplazamientos_plazas(csv_file):
    csvf = TextIOWrapper(csv_file, encoding="utf-8")
    reader = csv.reader(csvf)
    errors = []
    nombre = ""
    
    for index, row in enumerate(reader):

        if index < 1:
            continue
        if row[cdict["nombre"]]:
            nombre = row[cdict["nombre"]]

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
            errors.append(ValidationError(
                _("Error en la línea %(i)s: %(error)s"),
                params={"i": index+1, "error": e}
            ))
            continue

        new_plaza = models.Plaza(
            pk=row[cdict["pk"]],
            horario=row[cdict["horario"]],
            emplazamiento=new_emplazamiento)
        try:
            new_plaza.full_clean()
            new_plaza.save()
        except ValidationError as e:
            errors.append(ValidationError(
                _("Error en la línea %(i)s: %(error)s"),
                params={"i": index+1, "error": e}
            ))
        try:
            becario = models.Becario.objects.get(dni=row[cdict["dni"]])
            becario.plaza_asignada = new_plaza
            becario.save()
        except ObjectDoesNotExist:
            pass

    if errors:
        raise ValidationError(errors)    


# Métodos para comprobar si los campos del CSV son válidos

def is_codigo_tit(cod):
    return re.match(r"^[GMD]\d{3}$", cod)

def has_permisos(perm):
    return perm == "Sí"

def is_codigo_actividad(cod):
    return re.match(r"A\d{1,3}", cod)
