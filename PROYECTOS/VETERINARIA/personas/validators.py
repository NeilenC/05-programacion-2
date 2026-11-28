from django.core.exceptions import ValidationError


def validar_dni(valor):
    """El DNI son 8 dígitos (sin puntos)."""
    if not (valor.isdigit() and len(valor) == 8):
        raise ValidationError('El DNI tiene que tener 8 dígitos, sin puntos.')


def validar_cuit_cuil(valor):
    """CUIT/CUIL: 11 dígitos (sin guiones) con dígito verificador válido."""
    if not (valor.isdigit() and len(valor) == 11):
        raise ValidationError('El CUIT/CUIL tiene que tener 11 dígitos, sin guiones.')

    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(digito) * peso for digito, peso in zip(valor[:10], pesos))
    verificador = 11 - (suma % 11)
    if verificador == 11:
        verificador = 0
    elif verificador == 10:
        verificador = 9

    if verificador != int(valor[10]):
        raise ValidationError('El dígito verificador del CUIT/CUIL no es válido.')
