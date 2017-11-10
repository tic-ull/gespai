# coding=utf-8

import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


def dni_validator(dni):
    if is_dni(dni) or is_nie(dni):
        return
    else:
        raise ValidationError(
            _("DNI o NIE no válido: %(dni)s"),
            params = {"dni": dni}
        )

_DNI_PATRON_REGEX = r"^\d{8}[A-Z]$"
_DNI_VERIFICACION = "TRWAGMYFPDXBNJZSQVHLCKE"
_DNI_MODULO_VERIFICACION = 23
_DNI_REGEX = re.compile(_DNI_PATRON_REGEX)
def is_dni(dni):
    try:
        letra_verificacion = _DNI_VERIFICACION[int(dni[:-1]) % _DNI_MODULO_VERIFICACION]
    except:
        return False
    return _DNI_REGEX.match(dni) and letra_verificacion == dni[-1]

_NIE_PATRON_REGEX = r"^[XYZ]\d{7}[A-Z]$"
_NIE_LETRA_SUBSTITUCION = {"X": "0", "Y": "1", "Z": "2"}
_NIE_REGEX = re.compile(_NIE_PATRON_REGEX)
def is_nie(nie):
    try:
        nie_sub = _NIE_LETRA_SUBSTITUCION[nie[0]] + nie[1:-1]
        letra_verificacion = _DNI_VERIFICACION[int(nie_sub) % _DNI_MODULO_VERIFICACION]
    except Exception:
        return False
    return _NIE_REGEX.match(nie) and letra_verificacion == nie[-1]

def telefono_validator(telefono):
    # NOTE Preguntar cuáles son los formatos de teléfono
    # válidos, la posibilidad de teléfonos internaciona-
    # les cambia este validador
    if telefono.isdigit() and len(telefono) == 9:
        return 
    else:
        raise ValidationError(
            _("Teléfono no válido: %(telefono)s"),
            params = {"telefono": telefono}
        )
