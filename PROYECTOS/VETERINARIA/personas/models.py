from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from .validators import validar_cuit_cuil, validar_dni


class Persona(models.Model):
    """Tabla base: una persona física o una organización (persona jurídica).

    Ser dueño de una mascota no es un campo: es figurar en MascotaDuenio
    (app mascotas).
    """

    class MotivoSuspension(models.TextChoices):
        BAJA_VOLUNTARIA = 'BAJA', 'Baja voluntaria'
        FALLECIMIENTO = 'FALLECIMIENTO', 'Fallecimiento'
        DUPLICADO = 'DUPLICADO', 'Duplicado'
        OTRO = 'OTRO', 'Otro'

    nombre = models.CharField(max_length=100)
    cuit_cuil = models.CharField('CUIT/CUIL', max_length=11, unique=True,
                                 validators=[validar_cuit_cuil])
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)
    fecha_suspension = models.DateTimeField(null=True, blank=True)
    motivo_suspension = models.CharField(max_length=15, blank=True,
                                         choices=MotivoSuspension.choices)

    class Meta:
        verbose_name = 'persona'
        verbose_name_plural = 'personas'
        ordering = ['nombre']

    def clean(self):
        # Activo: los datos de suspensión van vacíos. Suspendido: van los dos.
        if self.activo and (self.fecha_suspension or self.motivo_suspension):
            raise ValidationError('Una persona activa no tiene fecha ni motivo de suspensión.')
        if not self.activo and not (self.fecha_suspension and self.motivo_suspension):
            raise ValidationError('Para suspender hay que completar la fecha y el motivo.')

    def __str__(self):
        # Si es física o jurídica, muestra el detalle (así se ve en los desplegables).
        for relacion in ('personafisica', 'personajuridica'):
            try:
                return str(getattr(self, relacion))
            except ObjectDoesNotExist:
                continue
        return self.nombre


class PersonaFisica(Persona):
    apellido = models.CharField(max_length=100)
    dni = models.CharField('DNI', max_length=8, unique=True, validators=[validar_dni])
    fecha_nacimiento = models.DateField()
    # Cuenta del portal (usuario de Django). Opcional: alguien que llega a la
    # veterinaria sin cuenta se carga igual. El nombre de usuario es el DNI.
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT,
                                null=True, blank=True,
                                related_name='persona_fisica'
                                )

    class Meta:
        verbose_name = 'persona física'
        verbose_name_plural = 'personas físicas'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.apellido}, {self.nombre} (DNI {self.dni})'


class PersonaJuridica(Persona):
    # Sin campos propios: el nombre de la organización va en Persona.nombre.
    # No tiene usuario, así que las organizaciones no entran al portal.

    class Meta:
        verbose_name = 'persona jurídica'
        verbose_name_plural = 'personas jurídicas'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} (CUIT {self.cuit_cuil})'


class Domicilio(models.Model):
    persona = models.OneToOneField(Persona,
                                   on_delete=models.CASCADE,
                                   related_name='domicilio'
                                   )
    localidad = models.ForeignKey('geografica.Localidad',
                                  on_delete=models.PROTECT,
                                  related_name='domicilios'
                                  )
    calle = models.CharField(max_length=150)
    altura = models.CharField(max_length=10)
    piso = models.CharField(max_length=10, blank=True)
    # Unidad dentro del edificio, no el departamento geográfico.
    departamento = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = 'domicilio'
        verbose_name_plural = 'domicilios'

    def __str__(self):
        direccion = f'{self.calle} {self.altura}'
        if self.piso:
            direccion += f', piso {self.piso}'
        if self.departamento:
            direccion += f', depto. {self.departamento}'
        return f'{direccion} - {self.localidad}'
