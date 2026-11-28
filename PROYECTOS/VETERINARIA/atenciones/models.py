from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Vacuna(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'vacuna'
        verbose_name_plural = 'vacunas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Medicamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'medicamento'
        verbose_name_plural = 'medicamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Atencion(models.Model):
    """Historia clínica. La mascota, el veterinario y el motivo salen del turno."""

    # Uno a uno: un turno tiene 0 o 1 atención (los pendientes y cancelados no tienen).
    turno = models.OneToOneField('turnos.Turno',
                                 on_delete=models.PROTECT,
                                 related_name='atencion'
                                 )
    fecha = models.DateTimeField(default=timezone.now)
    diagnostico = models.TextField('diagnóstico')

    class Meta:
        verbose_name = 'atención'
        verbose_name_plural = 'atenciones'
        ordering = ['-fecha']

    def clean(self):
        errores = {}
        if self.fecha and self.fecha > timezone.now():
            errores['fecha'] = 'La fecha de la atención no puede ser futura.'
        if self.turno_id:
            # Import acá adentro para no generar un import circular entre apps.
            from turnos.models import Turno
            if self.turno.estado != Turno.Estado.ATENDIDO:
                errores['turno'] = 'Solo un turno atendido puede tener atención.'
            elif self.pk is None and not self.turno.mascota.activa:
                errores['turno'] = 'La mascota está inactiva: no puede recibir atenciones nuevas.'
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f'Atención de {self.turno.mascota.nombre} ({self.fecha:%d/%m/%Y})'


class VacunaAplicada(models.Model):
    atencion = models.ForeignKey(Atencion,
                                 on_delete=models.PROTECT,
                                 related_name='vacunas_aplicadas'
                                 )
    vacuna = models.ForeignKey(Vacuna,
                               on_delete=models.PROTECT,
                               related_name='aplicaciones'
                               )
    fecha_aplicacion = models.DateField('fecha de aplicación')
    fecha_refuerzo = models.DateField('fecha de refuerzo', null=True, blank=True)

    class Meta:
        verbose_name = 'vacuna aplicada'
        verbose_name_plural = 'vacunas aplicadas'
        constraints = [
            # El refuerzo (si tiene) es posterior a la aplicación.
            models.CheckConstraint(
                condition=Q(fecha_refuerzo__isnull=True) | Q(fecha_refuerzo__gt=F('fecha_aplicacion')),
                name='refuerzo_posterior_a_aplicacion',
                violation_error_message='La fecha de refuerzo tiene que ser posterior a la de aplicación.',
            ),
        ]

    def __str__(self):
        return f'{self.vacuna} ({self.fecha_aplicacion:%d/%m/%Y})'


class Tratamiento(models.Model):
    atencion = models.ForeignKey(Atencion,
                                 on_delete=models.PROTECT,
                                 related_name='tratamientos'
                                 )
    medicamento = models.ForeignKey(Medicamento,
                                    on_delete=models.PROTECT,
                                    related_name='tratamientos'
                                    )
    dosis = models.CharField(max_length=100)
    duracion_dias = models.PositiveIntegerField('duración (días)')

    class Meta:
        verbose_name = 'tratamiento'
        verbose_name_plural = 'tratamientos'

    def __str__(self):
        return f'{self.medicamento} - {self.dosis} por {self.duracion_dias} días'
