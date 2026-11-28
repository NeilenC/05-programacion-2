from django.conf import settings
from django.db import models


class Veterinario(models.Model):
    """Modelo propio, independiente de Persona.

    Costo aceptado en el DER: una veterinaria que también es dueña se carga dos
    veces (en PersonaFisica para ser dueña y acá para atender).
    """

    # Opcional: un veterinario que no usa el sistema no necesita cuenta.
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   null=True, blank=True,
                                   related_name='veterinario'
                                   )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'veterinario'
        verbose_name_plural = 'veterinarios'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.apellido}, {self.nombre} (MP {self.matricula})'
