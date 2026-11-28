from django.contrib import admin

from .models import Veterinario


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'matricula', 'especialidad', 'usuario')
    search_fields = ['apellido', 'nombre', 'matricula']
