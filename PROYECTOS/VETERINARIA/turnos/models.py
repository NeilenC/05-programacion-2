from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Turno(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ATENDIDO = 'ATENDIDO', 'Atendido'
        CANCELADO = 'CANCELADO', 'Cancelado'

    mascota = models.ForeignKey('mascotas.Mascota',
                                on_delete=models.PROTECT,
                                related_name='turnos'
                                )
    veterinario = models.ForeignKey('veterinarios.Veterinario',
                                    on_delete=models.PROTECT,
                                    related_name='turnos'
                                    )
    # Quién sacó el turno: el dueño desde el portal o alguien del personal.
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='turnos_creados'
                                   )
    fecha_hora = models.DateTimeField('fecha y hora de inicio')
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=10, choices=Estado.choices,
                              default=Estado.PENDIENTE)

    class Meta:
        verbose_name = 'turno'
        verbose_name_plural = 'turnos'
        ordering = ['-fecha_hora']
        constraints = [
            # Un veterinario no puede tener dos turnos en el mismo bloque.
            models.UniqueConstraint(fields=['veterinario', 'fecha_hora'],
                                    name='un_turno_por_bloque_y_veterinario'),
        ]

    def clean(self):
        errores = {}

        # 1) La hora de inicio cae en la grilla de bloques fijos.
        if self.fecha_hora:
            hora = timezone.localtime(self.fecha_hora) if timezone.is_aware(self.fecha_hora) else self.fecha_hora
            minutos_del_dia = hora.hour * 60 + hora.minute
            duracion = settings.DURACION_TURNO_MINUTOS
            if minutos_del_dia % duracion or hora.second or hora.microsecond:
                errores['fecha_hora'] = f'El turno tiene que empezar en un bloque de {duracion} minutos.'

        # 2) Una mascota inactiva no recibe turnos nuevos.
        if self.pk is None and self.mascota_id and not self.mascota.activa:
            errores['mascota'] = 'La mascota está inactiva: no puede recibir turnos nuevos.'

        # 3) Atendido y Cancelado no vuelven atrás.
        if self.pk is not None:
            estado_anterior = Turno.objects.filter(pk=self.pk).values_list('estado', flat=True).first()
            if estado_anterior and estado_anterior != self.Estado.PENDIENTE and estado_anterior != self.estado:
                errores['estado'] = 'Un turno atendido o cancelado no puede cambiar de estado.'

        # 4) Solo un turno atendido puede tener atención.
        if self.estado != self.Estado.ATENDIDO and hasattr(self, 'atencion'):
            errores.setdefault('estado', 'Este turno ya tiene una atención cargada: tiene que quedar como atendido.')

        if errores:
            raise ValidationError(errores)

    def __str__(self):
        fecha = timezone.localtime(self.fecha_hora) if timezone.is_aware(self.fecha_hora) else self.fecha_hora
        return f'{fecha:%d/%m/%Y %H:%M} - {self.mascota.nombre} con {self.veterinario.apellido}'
