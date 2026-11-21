"""Aviso: entidad central de la rebanada. Coordina y delega en su estado."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from dominio.catalogos import GravedadEstimada, TipoSituacion, a_catalogo
from dominio.estados import EstadoAviso, Pendiente
from dominio.excepciones import AutorNoCorresponde
from dominio.nota import Nota

if TYPE_CHECKING:
    from dominio.usuarios import Operador, Reportante


class Aviso:
    """Un aviso nace pendiente (R1) y solo cambia por sus operaciones.

    Todo rechazo ocurre antes de modificar el objeto (R6). Los datos originales
    no tienen mutadores (R3) y la colección de notas no se expone (R2).
    """

    def __init__(
        self,
        id: UUID,
        ubicacion: str,
        situacion: TipoSituacion,
        gravedad: GravedadEstimada,
        descripcion: str,
        reportante: Reportante,
        fecha_registro: datetime,
        # Pendiente no guarda datos propios, por eso compartir la instancia es seguro.
        estado: EstadoAviso = Pendiente(),
    ) -> None:
        self._id = id
        self._ubicacion = ubicacion
        self._situacion = a_catalogo(TipoSituacion, situacion)
        self._gravedad = a_catalogo(GravedadEstimada, gravedad)
        self._descripcion = descripcion
        self._reportante = reportante
        self._fecha_registro = fecha_registro
        self._estado = estado
        self._notas: list[Nota] = []

    # --- consultas (propiedades de solo lectura) ---------------------------------

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def ubicacion(self) -> str:
        return self._ubicacion

    @property
    def situacion(self) -> TipoSituacion:
        return self._situacion

    @property
    def gravedad(self) -> GravedadEstimada:
        return self._gravedad

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def reportante(self) -> Reportante:
        return self._reportante

    @property
    def fecha_registro(self) -> datetime:
        return self._fecha_registro

    @property
    def estado(self) -> EstadoAviso:
        return self._estado

    def obtener_notas(self) -> tuple[Nota, ...]:
        return tuple(self._notas)

    # --- operaciones --------------------------------------------------------------

    def agregar_nota(self, nota: Nota) -> None:
        """R2: agrega una nota si el estado lo permite y el autor es el reportante."""
        self._estado.validar_agregado_nota()
        if nota.autor != self._reportante:
            raise AutorNoCorresponde()
        self._notas.append(nota)

    def descartar(
        self, operador: Operador, justificacion: str, fecha_hora: datetime
    ) -> None:
        """R4 y R5: el estado calcula el estado siguiente; recién ahí se asigna."""
        self._estado = self._estado.descartar(operador, justificacion, fecha_hora)
