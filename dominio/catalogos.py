"""Catálogos cerrados del enunciado (situaciones y gravedad)."""

from enum import Enum

from dominio.excepciones import ValorFueraDeCatalogo


class TipoSituacion(Enum):
    INUNDACION = "INUNDACION"
    INCENDIO = "INCENDIO"
    ACCIDENTE_VIAL = "ACCIDENTE_VIAL"


class GravedadEstimada(Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


def a_catalogo(catalogo: type[Enum], valor: object) -> Enum:
    """Convierte `valor` en un miembro de `catalogo` o lo rechaza."""
    try:
        return catalogo(valor)
    except ValueError:
        raise ValorFueraDeCatalogo(catalogo.__name__, valor) from None
