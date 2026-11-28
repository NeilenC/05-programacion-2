from django.contrib import admin

from .models import Turno


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'mascota', 'veterinario', 'estado', 'creado_por')
    list_filter = ('estado', 'veterinario')
    search_fields = ['mascota__nombre', 'veterinario__apellido', 'motivo']
    autocomplete_fields = ['mascota', 'veterinario']
    date_hierarchy = 'fecha_hora'
    exclude = ('creado_por',)

    def save_model(self, request, obj, form, change):
        # El turno cargado desde el admin lo crea el usuario logueado.
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
