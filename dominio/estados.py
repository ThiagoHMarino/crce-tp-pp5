"""Estados del aviso (patrón State).

Cada estado decide qué operaciones admite y a qué estado pasa. `Aviso` solo
delega: nunca pregunta en qué estado está para decidir.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from dominio.excepciones import EstadoNoPermiteOperacion, JustificacionInvalida

if TYPE_CHECKING:
    from dominio.usuarios import Operador


class EstadoAviso(ABC):
    """Contrato mínimo de un estado.

    Toda operación rechazada lanza una `ErrorDeDominio` (o una subclase) y no
    modifica nada: los estados no tienen efectos, solo devuelven el estado
    siguiente.
    """

    NOMBRE: str

    @abstractmethod
    def validar_agregado_nota(self) -> None:
        """Comprueba si el estado permite agregar una nota.

        Lanza `ErrorDeDominio` si no lo permite.
        """

    def descartar(
        self, operador: Operador, justificacion: str, fecha_hora: datetime
    ) -> EstadoAviso:
        """Devuelve el estado resultante de descartar el aviso.

        Por defecto rechaza (R5); `Pendiente` lo redefine.
        """
        raise EstadoNoPermiteOperacion(self.NOMBRE, "descartar")


class Pendiente(EstadoAviso):
    """Aviso sin evaluar: admite notas y puede descartarse.

    No guarda datos propios, por eso una misma instancia puede compartirse.
    """

    NOMBRE = "pendiente"

    def validar_agregado_nota(self) -> None:
        return None

    def descartar(
        self, operador: Operador, justificacion: str, fecha_hora: datetime
    ) -> EstadoAviso:
        if not (isinstance(justificacion, str) and justificacion.strip()):
            raise JustificacionInvalida()
        return Descartado(operador, justificacion, fecha_hora)


class Aceptado(EstadoAviso):
    """Aviso aceptado (terminal). La operación de aceptar queda fuera del Avance 1."""

    NOMBRE = "aceptado"

    def validar_agregado_nota(self) -> None:
        raise EstadoNoPermiteOperacion(self.NOMBRE, "agregar notas")


class Descartado(EstadoAviso):
    """Aviso descartado (terminal). Conserva operador, justificación y fecha."""

    NOMBRE = "descartado"

    def __init__(
        self, operador: Operador, justificacion: str, fecha_hora: datetime
    ) -> None:
        self._operador = operador
        self._justificacion = justificacion
        self._fecha_hora = fecha_hora

    @property
    def operador(self) -> Operador:
        return self._operador

    @property
    def justificacion(self) -> str:
        return self._justificacion

    @property
    def fecha_hora(self) -> datetime:
        return self._fecha_hora

    def validar_agregado_nota(self) -> None:
        raise EstadoNoPermiteOperacion(self.NOMBRE, "agregar notas")
