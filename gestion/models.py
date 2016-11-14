# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError

# Create your models here.

nombre_regex = r'^(?i)([a-zñÁÉÍÓÚáéíóú. ]{2,60})$'

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

    def __unicode__(self):
        return 'Plaza #' + unicode(self.pk) + ' - ' + self.get_horario_display()


class Becario(models.Model):
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
                              validators=[validators.RegexValidator(nombre_regex)])
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


class PrelacionBecario(models.Model):

    class Meta:
        # Un becario solo puede indicar su preferencia para una plaza una sola vez
        # Un becario solo puede indicar un orden de prelacion para cada plaza
        unique_together = (('becario', 'plaza'), ('becario', 'num_orden'))
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    plaza = models.ForeignKey(Plaza, on_delete=models.CASCADE)
    num_orden = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return unicode(self.becario) + '(' + unicode(self.num_orden) + ') - ' + unicode(self.plaza)


class PlanFormacion(models.Model):

    class Meta:
        # El mismo curso no puede impartirse dos veces el mismo día a la misma
        # hora
        unique_together = (('nombre_curso', 'fecha_imparticion'))
    nombre_curso = models.CharField(max_length=200)
    lugar_imparticion = models.CharField(max_length=200)
    fecha_imparticion = models.DateTimeField()

    def __unicode__(self):
        return self.nombre_curso + ' - ' + unicode(self.fecha_imparticion.date().strftime('%d/%m/%Y'))


class AsistenciaFormacion(models.Model):

    class Meta:
        unique_together = (('becario', 'curso'))
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    curso = models.ForeignKey(PlanFormacion, on_delete=models.CASCADE)
    calificacion = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True, default=None,
        validators=[validators.MinValueValidator(0.00), validators.MaxValueValidator(10.00)])

    def __unicode__(self):
        return unicode(self.becario) + ' - ' + unicode(self.curso)

class ResponsableAula(models.Model):
    nombre = models.CharField(max_length=200,
                              validators=[validators.RegexValidator(nombre_regex)])
    apellido1 = models.CharField(max_length=200)
    apellido2 = models.CharField(max_length=200, blank=True)
    dni = models.CharField(primary_key=True, validators=[dni_validator],
                           max_length=8)
    email = models.EmailField(unique=True)
    telefono = models.PositiveIntegerField(
        validators=[telefono_validator], blank=True, null=True)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE)

    def __unicode__(self):
        context = {
            'nombre': self.nombre,
            'apellido1': self.apellido1,
            'apellido2': self.apellido2,
        }
        return u'%(nombre)s %(apellido1)s %(apellido2)s' % context
