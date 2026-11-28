from django.db import models


class Especie(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'especie'
        verbose_name_plural = 'especies'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Raza(models.Model):
    # Cada especie tiene una raza "Mestizo".
    especie = models.ForeignKey(Especie,
                                on_delete=models.PROTECT,
                                related_name='razas'
                                )
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'raza'
        verbose_name_plural = 'razas'
        ordering = ['especie__nombre', 'nombre']
        constraints = [
            models.UniqueConstraint(fields=['especie', 'nombre'],
                                    name='raza_unica_por_especie'),
        ]

    def __str__(self):
        return f'{self.especie} - {self.nombre}'


class Mascota(models.Model):

    class Sexo(models.TextChoices):
        MACHO = 'M', 'Macho'
        HEMBRA = 'H', 'Hembra'

    raza = models.ForeignKey(Raza,
                             on_delete=models.PROTECT,
                             related_name='mascotas'
                             )
    nombre = models.CharField(max_length=50)
    sexo = models.CharField(max_length=1, choices=Sexo.choices)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso = models.DecimalField('peso (kg)', max_digits=5, decimal_places=2,
                               null=True, blank=True)
    color = models.CharField(max_length=50, blank=True)
    # Único pero opcional: null=True permite muchas mascotas sin microchip.
    microchip = models.CharField(max_length=20, unique=True, null=True, blank=True)
    castrado = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)
    # Atajo para llegar a los dueños: mascota.duenios.all().
    # La tabla intermedia es MascotaDuenio, que guarda es_principal.
    duenios = models.ManyToManyField('personas.Persona',
                                     through='MascotaDuenio',
                                     related_name='mascotas'
                                     )

    class Meta:
        verbose_name = 'mascota'
        verbose_name_plural = 'mascotas'
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        # Un microchip vacío se guarda como NULL para no chocar con el UNIQUE.
        if not self.microchip:
            self.microchip = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} ({self.raza})'


class MascotaDuenio(models.Model):
    """Une personas y mascotas (N:M). Ser dueño es tener una fila acá."""

    mascota = models.ForeignKey(Mascota,
                                on_delete=models.PROTECT,
                                related_name='mascota_duenios'
                                )
    persona = models.ForeignKey('personas.Persona',
                                on_delete=models.PROTECT,
                                related_name='mascota_duenios'
                                )
    es_principal = models.BooleanField('responsable principal', default=False)

    class Meta:
        verbose_name = 'dueño de la mascota'
        verbose_name_plural = 'dueños de la mascota'
        constraints = [
            models.UniqueConstraint(fields=['mascota', 'persona'],
                                    name='duenio_unico_por_mascota'),
            # Como máximo un responsable principal por mascota.
            # Que haya al menos uno se controla en el admin.
            models.UniqueConstraint(fields=['mascota'],
                                    condition=models.Q(es_principal=True),
                                    name='un_principal_por_mascota'),
        ]

    def __str__(self):
        principal = ' (principal)' if self.es_principal else ''
        return f'{self.persona} - {self.mascota.nombre}{principal}'
