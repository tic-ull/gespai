# coding=utf-8
from __future__ import unicode_literals
import datetime

from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings


nombre_regex = r'^(?i)([a-zñÁÉÍÓÚáéíóú. ]{2,60})$'

# Métodos para realizar validaciones

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

def codigo_tit_validator(codigo):
    if len(codigo) == 4:
        if codigo[0].isalpha and codigo[1:].isdigit():
            return
    raise ValidationError(
        _('Introduzca un codigo de titulacion valido'),
        params={'value': codigo},
    )

# Modelos

class Emplazamiento(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class Plaza(models.Model):
    HORARIOS = (
        ('M', 'Mañana'),
        ('T', 'Tarde'),
    )
    emplazamiento = models.ForeignKey(Emplazamiento, on_delete=models.CASCADE)
    horario = models.CharField(max_length=1, choices=HORARIOS)

    def __str__(self):
        return "Plaza #{0.pk}: {0.emplazamiento} - {0.horario}".format(self)

class Titulacion(models.Model):
    codigo = models.CharField(max_length=4, primary_key=True, validators=[codigo_tit_validator])
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Becario(models.Model):
    ESTADOS = (
        ("A", "Asignado"),
        ("S", "Suplente"),
        ("R", "Renuncia"),
        ("E", "Excluido"),
        ("N", "No asignado")
    )
    nombre = models.CharField(max_length=200,
                              validators=[validators.RegexValidator(nombre_regex)])
    apellido1 = models.CharField(max_length=200)
    apellido2 = models.CharField(max_length=200, blank=True)
    orden = models.PositiveIntegerField(unique=True)
    dni = models.CharField(primary_key=True, validators=[dni_validator],
                           max_length=8)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='N')
    titulacion = models.ForeignKey(Titulacion, on_delete=models.PROTECT)
    plaza_asignada = models.ForeignKey(Plaza, on_delete=models.SET_NULL,
                                       blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    telefono = models.PositiveIntegerField(
        validators=[telefono_validator], blank=True, null=True)
    permisos = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)

    def __init__(self, *args, **kwargs):
        super(Becario, self).__init__(*args, **kwargs)
        self.__plaza_previa = self.plaza_asignada

    def save(self, *args, **kwargs):
        # Si el becario pasa de no tener plaza a tener una
        if self.__plaza_previa == None and self.plaza_asignada != None:
            self.estado = "A"
            # Se crea una entrada en HistorialBecarios para este becario en este año.
            # Si existe una entrada para este becario en este año no se hace nada.
            hoy = datetime.datetime.now()
            if hoy.month < settings.MES_INICIO_CONV:
                conv, c = Convocatoria.objects.get_or_create(anyo_inicio=hoy.year - 1, anyo_fin=hoy.year)
            else:
                conv, c = Convocatoria.objects.get_or_create(anyo_inicio=hoy.year, anyo_fin=hoy.year + 1)
            HistorialBecarios.objects.get_or_create(dni_becario=self.dni, convocatoria=conv)
        # Si el becario pasa de tener una plaza a no tener una
        elif self.__plaza_previa != None and self.plaza_asignada == None:
            self.estado = "R"
            try:
                hoy = datetime.datetime.now()
                if hoy.month < settings.MES_INICIO_CONV:
                    conv, c = Convocatoria.objects.get_or_create(anyo_inicio=hoy.year - 1, anyo_fin=hoy.year)
                else:
                    conv, c = Convocatoria.objects.get_or_create(anyo_inicio=hoy.year, anyo_fin=hoy.year + 1)
                hist = HistorialBecarios.objects.get(dni_becario=self.dni, convocatoria=conv)
                hist.fecha_renuncia=datetime.datetime.now()
                hist.save()
            except ObjectDoesNotExist:
                # En el caso de que se intentase quitar una plaza a un becario
                # que no esté en HistorialBecarios no se hace ninguna acción
                # en la tabla HistorialBecarios
                pass
        super(Becario, self).save(*args, **kwargs)
        self.__plaza_previa = self.plaza_asignada

    def __str__(self):
        return "{0.nombre} {0.apellido1} {0.apellido2}".format(self)

class PreferenciasBecario(models.Model):

    class Meta:
        # Un becario solo puede indicar su preferencia para una plaza una sola vez
        # Un becario solo puede indicar un orden de prelacion para cada plaza
        unique_together = (('becario', 'plaza'), ('becario', 'num_orden'))
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    plaza = models.ForeignKey(Plaza, on_delete=models.CASCADE)
    num_orden = models.PositiveSmallIntegerField()

    def __str__(self):
        return (self.becario) + '(' + (self.num_orden) + ') - ' + (self.plaza)
        return "{0.becario}({0.num_orden}) - {0.plaza}".format(self)


class PlanFormacion(models.Model):

    codigo = models.CharField(primary_key=True, max_length=3)
    nombre_curso = models.CharField(max_length=200)
    lugar_imparticion = models.CharField(max_length=200, null=True, blank=True)
    fecha_imparticion = models.DateTimeField(null=True, blank=True)
    asistentes = models.ManyToManyField(Becario, through='AsistenciaFormacion')

    def __str__(self):
        if self.fecha_imparticion:
            return self.nombre_curso + ' - ' + (self.fecha_imparticion.date().strftime('%d/%m/%Y'))
        return self.nombre_curso


class AsistenciaFormacion(models.Model):

    class Meta:
        unique_together = (('becario', 'curso'))
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    curso = models.ForeignKey(PlanFormacion, on_delete=models.CASCADE)
    calificacion = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True, default=None,
        validators=[validators.MinValueValidator(0.00), validators.MaxValueValidator(10.00)])
    asistencia = models.BooleanField(default=False)

    def __str__(self):
        return "{0.becario} - {0.curso}".format(self)

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
    emplazamiento = models.ForeignKey(Emplazamiento, on_delete=models.CASCADE)

    def __str__(self):
        return "{0.nombre} {0.apellido1} {0.apellido2}".format(self)

class CambiosPendientes(models.Model):

    class Meta:
        # No puede haber dos cambios pendientes para el mismo becario en la
        # misma plaza para el mismo día.
        unique_together = (("becario", "plaza", "fecha_cambio"))
    ESTADOS = (
        ("A", "Asignado"),
        ("R", "Renuncia"),
        ("T", "Traslado"),
    )
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    # La plaza puede ser Null si se solicita una renuncia. Según el unique_together,
    # no podrá haber dos cambios para el mismo becario en el mismo día con la plaza a Null
    plaza = models.ForeignKey(Plaza, on_delete=models.CASCADE, null=True, blank=True)
    fecha_cambio = models.DateField(null=True, blank=True)
    estado_cambio = models.CharField(max_length=1, choices=ESTADOS)
    observaciones = models.TextField(blank=True)

    def clean(self):
        if hasattr(self, "becario") and self.estado_cambio == "A":
            entradas_historial = HistorialBecarios.objects.filter(dni_becario=self.becario.dni).count()
            if entradas_historial >= 5:
                raise ValidationError("El becario al que quiere asignar el cambio ya ha recibido beca en 5 convocatorias.")

    def __str__(self):
        if self.fecha_cambio:
            return "{0.becario} - {1} - {fecha}".format(self, get_estado_cambio_display(), fecha=fecha_cambio.strftime("%d/%m/%Y"))
        return "{0.becario} - {1}".format(self, get_estado_cambio_display())

class Convocatoria(models.Model):
    class Meta:
        unique_together = (("anyo_inicio", "anyo_fin"))
    ANYO_CHOICES = [(r,r) for r in range(2010, datetime.date.today().year + 20)]

    anyo_inicio = models.IntegerField(choices=ANYO_CHOICES, default=datetime.datetime.now().year)
    anyo_fin = models.IntegerField(choices=ANYO_CHOICES, default=datetime.datetime.now().year + 1)

    def clean(self):
        dif = self.anyo_fin - self.anyo_inicio
        if dif != 1:
            raise ValidationError("Convocatoria no válida")

    def __str__(self):
        return (self.anyo_inicio) + "/" + (self.anyo_fin)

class HistorialBecarios(models.Model):

    class Meta:
        unique_together = (("dni_becario", "convocatoria"))
    # No se usa una clave ajena pues al borrar un becario de la tabla Becarios
    # se perdería información en la tabla HistorialBecarios, la cual debe persistir
    dni_becario = models.CharField(validators=[dni_validator],max_length=8)
    convocatoria = models.ForeignKey(Convocatoria, on_delete=models.PROTECT)
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_renuncia = models.DateField(null=True, blank=True)

    def clean(self):
        entradas_historial = HistorialBecarios.objects.filter(dni_becario=self.dni_becario).count()
        if entradas_historial >= 5:
            raise ValidationError("Este becario ya ha sido asignado en 5 convocatorias.")

    def __str__(self):
        return (self.dni_becario) + " - " + (self.fecha_asignacion.strftime("%d/%m/%Y"))
