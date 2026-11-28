from django.contrib import admin

from .models import Persona, PersonaFisica, PersonaJuridica, Domicilio


class DomicilioInline(admin.StackedInline):
    model = Domicilio
    autocomplete_fields = ['localidad']
    extra = 0


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    # Necesario para buscar dueños con autocomplete desde Mascota.
    # Busca por nombre, DNI (física) o CUIT/CUIL.
    search_fields = ['nombre', 'personafisica__apellido', 'personafisica__dni', 'cuit_cuil']
    list_display = ('__str__', 'activo')

    def get_queryset(self, request):
        # Evita una consulta por fila al armar el texto "Apellido, Nombre (DNI ...)".
        return super().get_queryset(request).select_related('personafisica', 'personajuridica')

    def has_add_permission(self, request):
        # Las altas se hacen como persona física o jurídica.
        return False


@admin.register(PersonaFisica)
class PersonaFisicaAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'dni', 'telefono', 'activo')
    list_filter = ('activo',)
    search_fields = ['nombre', 'apellido', 'dni']
    inlines = [DomicilioInline]


@admin.register(PersonaJuridica)
class PersonaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cuit_cuil', 'telefono', 'activo')
    list_filter = ('activo',)
    search_fields = ['nombre', 'cuit_cuil']
    inlines = [DomicilioInline]
