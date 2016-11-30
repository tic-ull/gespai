from django.contrib import admin

# Register your models here.

from .models import (Becario, Plaza, Emplazamiento, PreferenciasBecario, PlanFormacion,
AsistenciaFormacion, ResponsableAula, CambiosPendientes, HistorialBecarios, Titulacion)

class BecarioAdmin(admin.ModelAdmin):
    list_display = ('orden', 'nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono',
    'plaza_asignada', 'estado', 'permisos')
    list_filter = ['plaza_asignada', 'titulacion', 'estado', 'permisos']
    search_fields = ['nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono']

class BecarioInline(admin.StackedInline):
    model = Becario
    extra = 0

class PlazaInline(admin.StackedInline):
    model = Plaza
    extra = 0

class PlazaAdmin(admin.ModelAdmin):
    list_display = ('id', 'emplazamiento', 'horario')
    inlines = [BecarioInline]

class EmplazamientoAdmin(admin.ModelAdmin):
    inlines = [PlazaInline]

class ResponsableAulaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido1', 'apellido2', 'emplazamiento', 'dni', 'email', 'telefono')
    list_filter = ['emplazamiento']
    search_fields = ['nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono']

class CambiosPendientesAdmin(admin.ModelAdmin):
    list_display = ('becario', 'plaza', 'fecha_cambio', 'estado_cambio')

class HistorialBecariosAdmin(admin.ModelAdmin):
    list_display = ('dni_becario', 'anyo', 'fecha_asignacion', 'fecha_renuncia')

class TitulacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')

class PlanFormacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre_curso', 'fecha_imparticion', 'lugar_imparticion')

class AsistenciaFormacionAdmin(admin.ModelAdmin):
    list_display = ('becario', 'curso', 'calificacion')
    list_filter = ['curso']

admin.site.register(Becario, BecarioAdmin)
admin.site.register(Plaza, PlazaAdmin)
admin.site.register(Emplazamiento, EmplazamientoAdmin)
admin.site.register(PreferenciasBecario)
admin.site.register(PlanFormacion, PlanFormacionAdmin)
admin.site.register(AsistenciaFormacion, AsistenciaFormacionAdmin)
admin.site.register(ResponsableAula, ResponsableAulaAdmin)
admin.site.register(CambiosPendientes, CambiosPendientesAdmin)
admin.site.register(HistorialBecarios, HistorialBecariosAdmin)
admin.site.register(Titulacion, TitulacionAdmin)
