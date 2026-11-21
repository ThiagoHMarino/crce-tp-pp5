"""Participantes de la rebanada: quien registra avisos y quien los descarta."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from dominio.aviso import Aviso
from dominio.catalogos import GravedadEstimada, TipoSituacion
from dominio.nota import Nota


@dataclass(frozen=True)
class Reportante:
    """Registra avisos y agrega notas a sus propios avisos."""

    id: int
    nombre: str

    def registrar_aviso(
        self,
        ubicacion: str,
        tipo_situacion: TipoSituacion,
        gravedad_estimada: GravedadEstimada,
        descripcion: str,
        fecha_hora: datetime,
    ) -> Aviso:
        return Aviso(
            id=uuid4(),
            ubicacion=ubicacion,
            situacion=tipo_situacion,
            gravedad=gravedad_estimada,
            descripcion=descripcion,
            reportante=self,
            fecha_registro=fecha_hora,
        )

    def agregar_nota(self, aviso: Aviso, texto: str, fecha_hora: datetime) -> None:
        aviso.agregar_nota(Nota(autor=self, fecha_hora=fecha_hora, texto=texto))


@dataclass(frozen=True)
class Operador:
    """Evalúa avisos. En este avance solo puede descartarlos."""

    id: int
    nombre: str

    def descartar_aviso(
        self, aviso: Aviso, justificacion: str, fecha_hora: datetime
    ) -> None:
        aviso.descartar(self, justificacion, fecha_hora)
