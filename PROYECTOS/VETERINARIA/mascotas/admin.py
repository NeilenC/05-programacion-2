from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Especie, Raza, Mascota, MascotaDuenio


class MascotaDuenioFormSet(BaseInlineFormSet):
    """Toda mascota tiene al menos un dueño y exactamente un principal."""

    def clean(self):
        super().clean()
        filas = [form.cleaned_data for form in self.forms
                 if form.cleaned_data and not form.cleaned_data.get('DELETE')]
        if not filas:
            raise ValidationError('La mascota tiene que tener al menos un dueño.')
        principales = sum(1 for fila in filas if fila.get('es_principal'))
        if principales != 1:
            raise ValidationError('Tiene que haber exactamente un responsable principal.')


class MascotaDuenioInline(admin.TabularInline):
    model = MascotaDuenio
    formset = MascotaDuenioFormSet
    autocomplete_fields = ['persona']
    extra = 1


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie')
    list_filter = ('especie',)
    search_fields = ['nombre', 'especie__nombre']


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'raza', 'sexo', 'castrado', 'activa')
    list_filter = ('activa', 'raza__especie', 'sexo', 'castrado')
    search_fields = ['nombre', 'microchip', 'duenios__nombre', 'duenios__personafisica__dni']
    autocomplete_fields = ['raza']
    inlines = [MascotaDuenioInline]
