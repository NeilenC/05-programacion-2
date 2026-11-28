from django.contrib import admin

from .models import PerfilSeguridad


@admin.register(PerfilSeguridad)
class PerfilSeguridadAdmin(admin.ModelAdmin):
    list_display = ('user', 'intentos_fallidos', 'bloqueado', 'debe_cambiar_clave')
    list_filter = ('bloqueado', 'debe_cambiar_clave')
    search_fields = ['user__username']
