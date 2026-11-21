from datetime import datetime

import pytest

from dominio.catalogos import GravedadEstimada, TipoSituacion
from dominio.usuarios import Operador, Reportante

FECHA = datetime(2026, 11, 20, 10, 0)
FECHA_POSTERIOR = datetime(2026, 11, 20, 10, 30)


@pytest.fixture
def ana() -> Reportante:
    return Reportante(id=1, nombre="Ana")


@pytest.fixture
def bruno() -> Reportante:
    return Reportante(id=2, nombre="Bruno")


@pytest.fixture
def operador() -> Operador:
    return Operador(id=10, nombre="Olga")


@pytest.fixture
def aviso(ana):
    return ana.registrar_aviso(
        ubicacion="Ruta 11 km 42",
        tipo_situacion=TipoSituacion.INCENDIO,
        gravedad_estimada=GravedadEstimada.ALTA,
        descripcion="Humo visible desde la ruta",
        fecha_hora=FECHA,
    )
