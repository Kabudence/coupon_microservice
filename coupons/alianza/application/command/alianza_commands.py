from __future__ import annotations

from datetime import datetime
from typing import Optional

from coupons.alianza.domain.entities.alianza import AlianzaData, AlianzaEstado
from coupons.alianza.infraestructure.repositories.alianza_repository import AlianzaRepository


class AlianzaCommandService:
    def __init__(self, repo: AlianzaRepository):
        self.repo = repo

    # ---- Solicitar ----
    def solicitar(self, solicitante_negocio_id: int, receptor_negocio_id: int, motivo: Optional[str] = None) -> AlianzaData:
        if solicitante_negocio_id == receptor_negocio_id:
            raise ValueError("No puede crear una alianza consigo mismo")

        # No duplicar si ya hay pendiente o aceptada entre las partes
        existing = self.repo.exists_between(solicitante_negocio_id, receptor_negocio_id)
        if existing and existing.estado in (AlianzaEstado.PENDIENTE, AlianzaEstado.ACEPTADA):
            raise ValueError("Ya existe una alianza pendiente o activa entre estos negocios")

        entity = AlianzaData(
            solicitante_negocio_id=solicitante_negocio_id,
            receptor_negocio_id=receptor_negocio_id,
            estado=AlianzaEstado.PENDIENTE,
            motivo=motivo,
            fecha_solicitud=datetime.utcnow(),
            fecha_respuesta=None,
        )
        return self.repo.create(entity)

    # ---- Transiciones de estado ----
    def aceptar(self, alianza_id: int, actor_negocio_id: int) -> AlianzaData:
        a = self.repo.get_by_id(alianza_id)
        if not a:
            raise ValueError("Alianza no encontrada")
        if a.estado != AlianzaEstado.PENDIENTE:
            raise ValueError("Solo se puede aceptar una alianza en estado PENDIENTE")
        if a.receptor_negocio_id != actor_negocio_id:
            raise ValueError("Solo el negocio receptor puede aceptar la alianza")
        return self.repo.change_estado(alianza_id, AlianzaEstado.ACEPTADA)

    def rechazar(self, alianza_id: int, actor_negocio_id: int, motivo: Optional[str] = None) -> AlianzaData:
        a = self.repo.get_by_id(alianza_id)
        if not a:
            raise ValueError("Alianza no encontrada")
        if a.estado != AlianzaEstado.PENDIENTE:
            raise ValueError("Solo se puede rechazar una alianza en estado PENDIENTE")
        if a.receptor_negocio_id != actor_negocio_id:
            raise ValueError("Solo el negocio receptor puede rechazar la alianza")
        return self.repo.change_estado(alianza_id, AlianzaEstado.RECHAZADA, motivo=motivo)

    def cancelar(self, alianza_id: int, actor_negocio_id: int, motivo: Optional[str] = None) -> AlianzaData:
        a = self.repo.get_by_id(alianza_id)
        if not a:
            raise ValueError("Alianza no encontrada")
        if a.estado != AlianzaEstado.PENDIENTE:
            raise ValueError("Solo se puede cancelar cuando está PENDIENTE")
        if a.solicitante_negocio_id != actor_negocio_id:
            raise ValueError("Solo el negocio solicitante puede cancelar su solicitud")
        return self.repo.change_estado(alianza_id, AlianzaEstado.CANCELADA, motivo=motivo)

    def suspender(self, alianza_id: int, actor_negocio_id: int, motivo: Optional[str] = None) -> AlianzaData:
        a = self.repo.get_by_id(alianza_id)
        if not a:
            raise ValueError("Alianza no encontrada")
        if a.estado != AlianzaEstado.ACEPTADA:
            raise ValueError("Solo se puede suspender una alianza ACTIVA")
        # Cualquiera de los dos puede suspender
        if actor_negocio_id not in (a.solicitante_negocio_id, a.receptor_negocio_id):
            raise ValueError("Solo los negocios involucrados pueden suspender la alianza")
        return self.repo.change_estado(alianza_id, AlianzaEstado.SUSPENDIDA, motivo=motivo)

    def reactivar(self, alianza_id: int, actor_negocio_id: int, motivo: Optional[str] = None) -> AlianzaData:
        a = self.repo.get_by_id(alianza_id)
        if not a:
            raise ValueError("Alianza no encontrada")
        if a.estado != AlianzaEstado.SUSPENDIDA:
            raise ValueError("Solo se puede reactivar una alianza SUSPENDIDA")
        if actor_negocio_id not in (a.solicitante_negocio_id, a.receptor_negocio_id):
            raise ValueError("Solo los negocios involucrados pueden reactivar la alianza")
        return self.repo.change_estado(alianza_id, AlianzaEstado.ACEPTADA, motivo=motivo)

    # ---- Utilidades ----
    def actualizar_motivo(self, alianza_id: int, actor_negocio_id: int, motivo: str) -> AlianzaData:
        a = self.repo.get_by_id(alianza_id)
        if not a:
            raise ValueError("Alianza no encontrada")
        if actor_negocio_id not in (a.solicitante_negocio_id, a.receptor_negocio_id):
            raise ValueError("Solo los negocios involucrados pueden modificar el motivo")
        a.motivo = motivo.strip() if motivo else None
        return self.repo.update(a)
