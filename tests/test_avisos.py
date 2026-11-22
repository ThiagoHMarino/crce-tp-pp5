"""Avance 1: avisos y notas. Cada test lleva el prefijo de la regla que verifica."""

from dataclasses import FrozenInstanceError
from datetime import datetime
from uuid import uuid4

import pytest

from dominio.aviso import Aviso
from dominio.catalogos import GravedadEstimada, TipoSituacion
from dominio.estados import Aceptado, Descartado, Pendiente
from dominio.excepciones import (
    AutorNoCorresponde,
    ErrorCRCE,
    EstadoNoPermiteOperacion,
    JustificacionInvalida,
    TextoDeNotaInvalido,
    ValorFueraDeCatalogo,
)
from tests.conftest import FECHA, FECHA_POSTERIOR


# --- R1: el aviso nace pendiente, con todos sus datos --------------------------------

def test_r1_aviso_nace_pendiente_con_sus_datos(aviso, ana):
    assert isinstance(aviso.estado, Pendiente)
    assert aviso.ubicacion == "Ruta 11 km 42"
    assert aviso.situacion is TipoSituacion.INCENDIO
    assert aviso.gravedad is GravedadEstimada.ALTA
    assert aviso.descripcion == "Humo visible desde la ruta"
    assert aviso.reportante == ana
    assert aviso.fecha_registro == FECHA
    assert aviso.obtener_notas() == ()


def test_r1_situacion_fuera_de_catalogo_se_rechaza(ana):
    with pytest.raises(ValorFueraDeCatalogo):
        ana.registrar_aviso("Centro", "TERREMOTO", GravedadEstimada.BAJA, "x", FECHA)


def test_r1_cada_aviso_nace_con_su_propio_estado_pendiente(ana):
    a1 = ana.registrar_aviso("A", TipoSituacion.INCENDIO, GravedadEstimada.ALTA, "d", FECHA)
    a2 = ana.registrar_aviso("B", TipoSituacion.INCENDIO, GravedadEstimada.ALTA, "d", FECHA)

    assert isinstance(a1.estado, Pendiente)
    assert isinstance(a2.estado, Pendiente)
    assert a1.estado is not a2.estado


# --- R2: notas del reportante sobre su aviso pendiente --------------------------------

def test_r2_reportante_agrega_nota_a_su_aviso_pendiente(aviso, ana):
    ana.agregar_nota(aviso, "Se ve más humo", FECHA_POSTERIOR)

    (nota,) = aviso.obtener_notas()
    assert nota.autor == ana
    assert nota.texto == "Se ve más humo"
    assert nota.fecha_hora == FECHA_POSTERIOR


def test_r2_dos_notas_se_conservan_en_orden_de_llegada(aviso, ana):
    segunda_fecha = datetime(2026, 11, 20, 11, 0)
    ana.agregar_nota(aviso, "Primera", FECHA_POSTERIOR)
    ana.agregar_nota(aviso, "Segunda", segunda_fecha)

    primera, segunda = aviso.obtener_notas()
    assert (primera.texto, primera.fecha_hora) == ("Primera", FECHA_POSTERIOR)
    assert (segunda.texto, segunda.fecha_hora) == ("Segunda", segunda_fecha)


def test_r2_otro_reportante_no_puede_agregar_notas(aviso, bruno):
    with pytest.raises(AutorNoCorresponde):
        bruno.agregar_nota(aviso, "Yo también lo vi", FECHA_POSTERIOR)

    assert aviso.obtener_notas() == ()


def test_r2_nota_vacia_se_rechaza_y_no_queda_registrada(aviso, ana):
    with pytest.raises(TextoDeNotaInvalido):
        ana.agregar_nota(aviso, "   ", FECHA_POSTERIOR)

    assert aviso.obtener_notas() == ()


def test_r2_las_notas_no_se_modifican_desde_afuera(aviso, ana):
    ana.agregar_nota(aviso, "Primera", FECHA_POSTERIOR)

    notas = aviso.obtener_notas()
    assert isinstance(notas, tuple)
    with pytest.raises(AttributeError):
        notas.append("intrusa")  # type: ignore[attr-defined]
    assert len(aviso.obtener_notas()) == 1


# --- R3: los datos originales no se modifican -----------------------------------------

def test_r3_datos_originales_son_de_solo_lectura(aviso):
    with pytest.raises(AttributeError):
        aviso.ubicacion = "Otra"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        aviso.reportante = None  # type: ignore[misc]


def test_r3_agregar_nota_no_cambia_los_datos_originales(aviso, ana):
    antes = (
        aviso.id, aviso.ubicacion, aviso.situacion, aviso.gravedad,
        aviso.descripcion, aviso.reportante, aviso.fecha_registro,
    )

    ana.agregar_nota(aviso, "Se ve más humo", FECHA_POSTERIOR)

    despues = (
        aviso.id, aviso.ubicacion, aviso.situacion, aviso.gravedad,
        aviso.descripcion, aviso.reportante, aviso.fecha_registro,
    )
    assert despues == antes


def test_r3_nota_es_inmutable(aviso, ana):
    ana.agregar_nota(aviso, "Texto", FECHA_POSTERIOR)
    (nota,) = aviso.obtener_notas()

    with pytest.raises(FrozenInstanceError):
        nota.texto = "Cambiado"  # type: ignore[misc]


# --- R4: descartar exige operador y justificación -------------------------------------

def test_r4_operador_descarta_con_justificacion(aviso, operador):
    operador.descartar_aviso(aviso, "Falsa alarma confirmada", FECHA_POSTERIOR)

    estado = aviso.estado
    assert isinstance(estado, Descartado)
    assert estado.operador == operador
    assert estado.justificacion == "Falsa alarma confirmada"
    assert estado.fecha_hora == FECHA_POSTERIOR


@pytest.mark.parametrize("justificacion", ["", "   ", None])
def test_r4_descartar_sin_justificacion_se_rechaza_y_sigue_pendiente(
    aviso, operador, justificacion
):
    with pytest.raises(JustificacionInvalida):
        operador.descartar_aviso(aviso, justificacion, FECHA_POSTERIOR)

    assert isinstance(aviso.estado, Pendiente)


@pytest.mark.parametrize("justificacion", ["", "   ", None])
def test_r4_descartado_no_puede_existir_sin_justificacion(operador, justificacion):
    with pytest.raises(JustificacionInvalida):
        Descartado(operador, justificacion, FECHA_POSTERIOR)


# --- R5: un aviso que ya no está pendiente no admite más operaciones ------------------

def test_r5_no_se_agregan_notas_a_un_aviso_descartado(aviso, ana, operador):
    operador.descartar_aviso(aviso, "Duplicado", FECHA_POSTERIOR)

    with pytest.raises(EstadoNoPermiteOperacion):
        ana.agregar_nota(aviso, "Tarde", datetime(2026, 11, 20, 11, 0))

    assert aviso.obtener_notas() == ()


def test_r5_no_se_descarta_dos_veces_y_se_conserva_el_primer_descarte(
    aviso, operador
):
    operador.descartar_aviso(aviso, "Primer motivo", FECHA_POSTERIOR)
    estado_previo = aviso.estado

    with pytest.raises(EstadoNoPermiteOperacion):
        operador.descartar_aviso(aviso, "Segundo motivo", datetime(2026, 11, 20, 12))

    assert aviso.estado is estado_previo
    assert aviso.estado.justificacion == "Primer motivo"


@pytest.fixture
def aviso_aceptado(ana):
    """Sin implementar aceptar(): se inyecta el estado Aceptado al construir."""
    return Aviso(
        id=uuid4(),
        ubicacion="Barrio Norte",
        situacion=TipoSituacion.INUNDACION,
        gravedad=GravedadEstimada.MEDIA,
        descripcion="Calles anegadas",
        reportante=ana,
        fecha_registro=FECHA,
        estado=Aceptado(),
    )


def test_r5_no_se_agregan_notas_a_un_aviso_aceptado(aviso_aceptado, ana):
    with pytest.raises(EstadoNoPermiteOperacion):
        ana.agregar_nota(aviso_aceptado, "Tarde", FECHA_POSTERIOR)

    assert aviso_aceptado.obtener_notas() == ()
    assert isinstance(aviso_aceptado.estado, Aceptado)


def test_r5_un_aviso_aceptado_no_puede_descartarse(aviso_aceptado, operador):
    with pytest.raises(EstadoNoPermiteOperacion):
        operador.descartar_aviso(aviso_aceptado, "Motivo", FECHA_POSTERIOR)

    assert isinstance(aviso_aceptado.estado, Aceptado)


# --- R6: una operación rechazada no deja cambios parciales ----------------------------

def test_r6_rechazos_son_errores_de_dominio_y_no_alteran_el_aviso(
    aviso, ana, bruno, operador
):
    ana.agregar_nota(aviso, "Válida", FECHA_POSTERIOR)
    estado_previo = aviso.estado
    notas_previas = aviso.obtener_notas()

    with pytest.raises(ErrorCRCE):
        bruno.agregar_nota(aviso, "Ajena", FECHA_POSTERIOR)
    with pytest.raises(ErrorCRCE):
        operador.descartar_aviso(aviso, "", FECHA_POSTERIOR)

    assert aviso.estado is estado_previo
    assert aviso.obtener_notas() == notas_previas


def test_r6_avisos_distintos_no_comparten_notas(ana):
    a1 = ana.registrar_aviso("A", TipoSituacion.INUNDACION, GravedadEstimada.BAJA, "d", FECHA)
    a2 = ana.registrar_aviso("B", TipoSituacion.INUNDACION, GravedadEstimada.BAJA, "d", FECHA)

    ana.agregar_nota(a1, "Solo en a1", FECHA_POSTERIOR)

    assert a1.id != a2.id
    assert a2.obtener_notas() == ()
    assert isinstance(a2, Aviso)
