"""Nota de texto que un reportante agrega a un aviso pendiente."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from dominio.excepciones import TextoDeNotaInvalido

if TYPE_CHECKING:
    from dominio.usuarios import Reportante


@dataclass(frozen=True)
class Nota:
    """Valor inmutable: nace completa (autor, fecha y hora, texto) o no nace."""

    autor: Reportante
    fecha_hora: datetime
    texto: str

    def __post_init__(self) -> None:
        if not (isinstance(self.texto, str) and self.texto.strip()):
            raise TextoDeNotaInvalido()
