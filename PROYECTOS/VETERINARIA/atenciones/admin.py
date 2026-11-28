from django.contrib import admin

from .models import Vacuna, Medicamento, Atencion, VacunaAplicada, Tratamiento


class VacunaAplicadaInline(admin.TabularInline):
    model = VacunaAplicada
    autocomplete_fields = ['vacuna']
    extra = 0


class TratamientoInline(admin.TabularInline):
    model = Tratamiento
    autocomplete_fields = ['medicamento']
    extra = 0


@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(Atencion)
class AtencionAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'turno')
    search_fields = ['turno__mascota__nombre', 'diagnostico']
    autocomplete_fields = ['turno']
    inlines = [VacunaAplicadaInline, TratamientoInline]

    def has_delete_permission(self, request, obj=None):
        # Las atenciones no se borran.
        return False
