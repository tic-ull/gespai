#coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError

# Create your models here.

def dni_validator(dni):
    if len(dni) == 8:
        if (dni[0].isalpha() and dni[1:].isdigit()) or dni.isdigit():
            return
    raise ValidationError(
        _('Introduzca un DNI válido'),
        params={'value': dni},
    )

def telefono_validator(telefono):
    if len(str(telefono)) != 9:
        raise ValidationError(
            _('Introduzca un número de teléfono válido'),
            params={'value': telefono},
        )

class Centro(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Plaza(models.Model):
    HORARIOS = (
        ('M', 'Mañana'),
        ('T', 'Tarde'),
    )
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE)
    horario = models.CharField(max_length=1, choices=HORARIOS)

    def __str__(self):
        return "Plaza #" + str(self.pk) + " - " + self.get_horario_display()

class Becario(models.Model):
    regex = r'^(?i)([a-zñÁÉÍÓÚáéíóú. ]{2,60})$'
    ESTADOS = (
        ('A', 'Asignado'),
        ('S', 'Suplente'),
        ('R', 'Renuncia'),
        ('E', 'Excluido'),
        ('N', 'No asignado')
    )
    HORARIOS = (
        ('M', 'Mañana'),
        ('T', 'Tarde'),
        ('N', 'No asignado'),
    )
    nombre = models.CharField(max_length=200,
                              validators=[validators.RegexValidator(regex)])
    apellido1 = models.CharField(max_length=200)
    apellido2 = models.CharField(max_length=200, blank=True)
    dni = models.CharField(primary_key=True, validators=[dni_validator],
                           max_length=8)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='N')
    titulacion = models.CharField(max_length=500)
    plaza_asignada = models.ForeignKey(Plaza, on_delete=models.SET_NULL,
                                        blank=True, null=True)
    horario_asignado = models.CharField(max_length=1, choices=HORARIOS,
                                        default="N")
    email = models.EmailField(unique=True)
    telefono = models.PositiveIntegerField(
        validators=[telefono_validator], blank=True, null=True)

    # para redirigir al crear o editar un usuario en un form
    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'pk': self.pk})

    '''
    def __str__(self):
        return self.nombre + ' ' + self.apellido1 + ' ' + self.apellido2
    '''

    def __unicode__(self):
        context = {
            'nombre': self.nombre,
            'apellido1': self.apellido1,
            'apellido2': self.apellido2,
        }
        return u'%(nombre)s %(apellido1)s %(apellido2)s' % context
