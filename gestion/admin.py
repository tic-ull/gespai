from django.contrib import admin

# Register your models here.

from .models import (Becario, Plaza, Centro, PrelacionBecario, PlanFormacion,
AsistenciaFormacion, ResponsableAula, CambiosPendientes, HistorialBecarios)

class BecarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono',
    'plaza_asignada', 'estado', 'permisos')
    list_filter = ['plaza_asignada', 'titulacion', 'horario_asignado', 'estado', 'permisos']
    search_fields = ['nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono']

class BecarioInline(admin.StackedInline):
    model = Becario
    extra = 0

class PlazaInline(admin.StackedInline):
    model = Plaza
    extra = 0

class PlazaAdmin(admin.ModelAdmin):
    inlines = [BecarioInline]

class CentroAdmin(admin.ModelAdmin):
    inlines = [PlazaInline]

class ResponsableAulaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido1', 'apellido2', 'centro', 'dni', 'email', 'telefono')
    list_filter = ['centro']
    search_fields = ['nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono']

class CambiosPendientesAdmin(admin.ModelAdmin):
    list_display = ('becario', 'plaza', 'fecha_cambio', 'estado_cambio')

class HistorialBecariosAdmin(admin.ModelAdmin):
    list_display = ('dni_becario', 'fecha_asignacion', 'fecha_renuncia')

admin.site.register(Becario, BecarioAdmin)
admin.site.register(Plaza, PlazaAdmin)
admin.site.register(Centro, CentroAdmin)
admin.site.register(PrelacionBecario)
admin.site.register(PlanFormacion)
admin.site.register(AsistenciaFormacion)
admin.site.register(ResponsableAula, ResponsableAulaAdmin)
admin.site.register(CambiosPendientes, CambiosPendientesAdmin)
admin.site.register(HistorialBecarios, HistorialBecariosAdmin)
