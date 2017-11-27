# coding=utf-8

import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator, \
    RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from gespai import validation

_NOMBRE_REGEX = r'^(?i)([a-zñÁÉÍÓÚáéíóú. ]{2,60})$'

# Modelos

class Emplazamiento(models.Model):
    
    _MAX_LENGTH_NOMBRE = 200

    nombre = models.CharField(max_length=_MAX_LENGTH_NOMBRE)

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
    class Meta:
        verbose_name = "titulación"
        verbose_name_plural = "titulaciones"
    _TITULACION_PATRON_REGEX = r"[GMD]\d{3}"

    codigo = models.CharField(max_length=4, primary_key=True, validators=[RegexValidator(_TITULACION_PATRON_REGEX)])
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Becario(models.Model):

    _NOMBRE_MAX_LENGTH = 200
    _DNI_MAX_LENGTH = 9

    ESTADOS = (
        ("A", "Asignado"),
        ("S", "Suplente"),
        ("R", "Renuncia"),
        ("E", "Excluido"),
        ("N", "No asignado")
    )
    nombre = models.CharField(
             max_length=_NOMBRE_MAX_LENGTH,
             validators=[RegexValidator(_NOMBRE_REGEX)])
    apellido1 = models.CharField(
                max_length=_NOMBRE_MAX_LENGTH,
                validators=[RegexValidator(_NOMBRE_REGEX)])
    apellido2 = models.CharField(
                max_length=_NOMBRE_MAX_LENGTH,
                blank=True,
                validators=[RegexValidator(_NOMBRE_REGEX)])
    orden = models.PositiveIntegerField(unique=True)
    dni = models.CharField(primary_key=True,
                           validators=[validation.dni_validator],
                           max_length=_DNI_MAX_LENGTH)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='N')
    titulacion = models.ForeignKey(Titulacion, on_delete=models.PROTECT)
    plaza_asignada = models.OneToOneField(Plaza, on_delete=models.SET_NULL,
                                       blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15,
        validators=[validation.telefono_validator], blank=True, null=True)
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
        unique_together = (('becario', 'plaza'), ('becario', 'orden'))
        verbose_name_plural = "preferencias becarios"
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    plaza = models.ForeignKey(Plaza, on_delete=models.CASCADE)
    orden = models.PositiveSmallIntegerField()

    def __str__(self):
        return "{0.becario}({0.orden}) - {0.plaza}".format(self)


class PlanFormacion(models.Model):

    class Meta:
        verbose_name = "plan de formación"
        verbose_name_plural = "planes de formación"

    codigo = models.CharField(primary_key=True, max_length=3)
    nombre_curso = models.CharField(max_length=200)
    lugar_imparticion = models.CharField(max_length=200, null=True, blank=True)
    fecha_imparticion = models.DateTimeField(null=True, blank=True)
    asistentes = models.ManyToManyField(Becario, through='AsistenciaFormacion')

    def __str__(self):
        if self.fecha_imparticion:
            return "{0.nombre_curso} - {fecha}".format(self, fecha=self.fecha_imparticion.date().strftime('%d/%m/%Y'))
        return self.nombre_curso


class AsistenciaFormacion(models.Model):

    class Meta:
        unique_together = (('becario', 'curso'))
        verbose_name = "asistencia formación"
        verbose_name_plural = "asistencias formación"
    becario = models.ForeignKey(Becario, on_delete=models.CASCADE)
    curso = models.ForeignKey(PlanFormacion, on_delete=models.CASCADE)
    calificacion = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True, default=None,
        validators=[MinValueValidator(0.00), MaxValueValidator(10.00)])
    asistencia = models.BooleanField(default=False)

    def __str__(self):
        return "{0.becario} - {0.curso}".format(self)

class ResponsableAula(models.Model):

    class Meta:
        verbose_name = "responsable de aula"
        verbose_name_plural = "responsables de aula"
    nombre = models.CharField(max_length=200,
                              validators=[RegexValidator(_NOMBRE_REGEX)])
    apellido1 = models.CharField(max_length=200)
    apellido2 = models.CharField(max_length=200, blank=True)
    dni = models.CharField(primary_key=True, validators=[validation.dni_validator],
                           max_length=8)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15,
        validators=[validation.telefono_validator], blank=True, null=True)
    emplazamiento = models.ForeignKey(Emplazamiento, on_delete=models.CASCADE)

    def __str__(self):
        return "{0.nombre} {0.apellido1} {0.apellido2}".format(self)

class CambiosPendientes(models.Model):

    class Meta:
        # No puede haber dos cambios pendientes para el mismo becario en la
        # misma plaza para el mismo día.
        unique_together = (("becario", "plaza", "fecha_cambio"))
        verbose_name = "cambio pendiente"
        verbose_name_plural = "cambios pendientes"
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
            return "{0.becario} - {1} - {fecha}".format(self, self.get_estado_cambio_display(), fecha=self.fecha_cambio.strftime("%d/%m/%Y"))
        return "{0.becario} - {1}".format(self, self.get_estado_cambio_display())

class Convocatoria(models.Model):

    _ANYO_COMIENZO = 2012
    _ANYO_CHOICES = [(r, r) for r in range(_ANYO_COMIENZO, datetime.date.today().year + 20)]

    class Meta:
        unique_together = (("anyo_inicio", "anyo_fin"))

    anyo_inicio = models.IntegerField(choices=_ANYO_CHOICES, default=datetime.datetime.now().year)
    anyo_fin = models.IntegerField(choices=_ANYO_CHOICES, default=datetime.datetime.now().year + 1)

    def clean(self):
        dif = self.anyo_fin - self.anyo_inicio
        if dif != 1:
            raise ValidationError(
                _("Convocatoria no válida"),
                params={"convocatoria": self.convocatoria})

    def __str__(self):
        return "{0.anyo_inicio}/{0.anyo_fin}".format(self)

class HistorialBecarios(models.Model):

    _DNI_MAX_LENGTH = 9
    _MAX_CONVOCATORIAS = 5

    class Meta:
        unique_together = (("dni_becario", "convocatoria"))
        verbose_name_plural = "historiales becarios"
    # No se usa una clave ajena pues al borrar un becario de la tabla Becarios
    # se perdería información en la tabla HistorialBecarios, la cual debe persistir
    dni_becario = models.CharField(validators=[validation.dni_validator], max_length=_DNI_MAX_LENGTH)
    convocatoria = models.ForeignKey(Convocatoria, on_delete=models.PROTECT)
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_renuncia = models.DateField(null=True, blank=True)

    def clean(self):
        entradas_historial = HistorialBecarios.objects.filter(dni_becario=self.dni_becario).count()
        if entradas_historial >= self._MAX_CONVOCATORIAS:
            raise ValidationError("Este becario ya ha sido asignado en 5 convocatorias.")

    def __str__(self):
        return "(0.dni_becario) - {fecha}".format(self, fecha=self.fecha_asignacion.strftime("%d/%m/%Y"))
