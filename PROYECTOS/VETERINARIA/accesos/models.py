from django.conf import settings
from django.db import models


class PerfilSeguridad(models.Model):
    """Datos de seguridad del usuario de Django (no se dibuja en el DER).

    El usuario en sí es el de Django (auth_user): no se escribe ningún modelo
    Usuario. El nombre de usuario es el DNI de la persona física.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='perfil_seguridad'
                                )
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    bloqueado = models.BooleanField(default=False)
    # True cuando tiene la clave inicial o vencida: tiene que cambiarla al entrar.
    debe_cambiar_clave = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'perfil de seguridad'
        verbose_name_plural = 'perfiles de seguridad'

    def __str__(self):
        return f'Seguridad de {self.user}'
