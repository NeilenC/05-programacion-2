from django.contrib import admin

from .models import Provincia, Departamento, Localidad


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'provincia')
    list_filter = ('provincia',)
    search_fields = ['nombre']


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento')
    search_fields = ['nombre', 'departamento__nombre']
    autocomplete_fields = ['departamento']
