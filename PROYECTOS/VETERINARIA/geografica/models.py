from django.db import models


class Provincia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'provincia'
        verbose_name_plural = 'provincias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    provincia = models.ForeignKey(Provincia,
                                  on_delete=models.PROTECT,
                                  related_name='departamentos'
                                  )
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'departamento'
        verbose_name_plural = 'departamentos'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['provincia', 'nombre'],
                                    name='departamento_unico_por_provincia'),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.provincia})'


class Localidad(models.Model):
    departamento = models.ForeignKey(Departamento,
                                     on_delete=models.PROTECT,
                                     related_name='localidades'
                                     )
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'localidad'
        verbose_name_plural = 'localidades'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['departamento', 'nombre'],
                                    name='localidad_unica_por_departamento'),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.departamento.nombre})'
