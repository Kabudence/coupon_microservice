from __future__ import annotations

from enum import Enum
from datetime import datetime
from typing import Optional


class AlianzaEstado(Enum):
    PENDIENTE = "PENDIENTE"
    ACEPTADA = "ACEPTADA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"
    SUSPENDIDA = "SUSPENDIDA"


class AlianzaData:
    def __init__(
        self,
        id: Optional[int] = None,
        solicitante_negocio_id: int | None = None,
        receptor_negocio_id: int | None = None,
        estado: AlianzaEstado | str = AlianzaEstado.PENDIENTE,
        motivo: Optional[str] = None,
        fecha_solicitud: Optional[datetime] = None,
        fecha_respuesta: Optional[datetime] = None,
    ):
        # Requeridos
        if solicitante_negocio_id is None or receptor_negocio_id is None:
            raise ValueError("solicitante_negocio_id y receptor_negocio_id son requeridos")
        if solicitante_negocio_id == receptor_negocio_id:
            raise ValueError("No puede crear una alianza consigo mismo (ids iguales)")

        # Normalización de estado
        self.estado = estado if isinstance(estado, AlianzaEstado) else AlianzaEstado(str(estado))

        # Asignación
        self.id = id
        self.solicitante_negocio_id = int(solicitante_negocio_id)
        self.receptor_negocio_id = int(receptor_negocio_id)
        self.motivo = (motivo.strip() if motivo else None)

        self.fecha_solicitud = fecha_solicitud or datetime.utcnow()
        self.fecha_respuesta = fecha_respuesta

        # Reglas simples de coherencia de fechas
        if self.estado != AlianzaEstado.PENDIENTE and self.fecha_respuesta is None:
            # Para estados finales o suspendida, si llega sin fecha_respuesta, la ponemos ahora
            self.fecha_respuesta = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "solicitante_negocio_id": self.solicitante_negocio_id,
            "receptor_negocio_id": self.receptor_negocio_id,
            "estado": self.estado.value if isinstance(self.estado, AlianzaEstado) else self.estado,
            "motivo": self.motivo,
            "fecha_solicitud": self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            "fecha_respuesta": self.fecha_respuesta.isoformat() if self.fecha_respuesta else None,
        }
