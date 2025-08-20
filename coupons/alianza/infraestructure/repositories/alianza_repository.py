from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from peewee import fn

from coupons.alianza.domain.entities.alianza import AlianzaData, AlianzaEstado
from coupons.alianza.infraestructure.model.alianza_model import AlianzaModel


class AlianzaRepository:
    # ---- mapping ----
    def _to_entity(self, rec: AlianzaModel) -> AlianzaData:
        return AlianzaData(
            id=rec.id,
            solicitante_negocio_id=rec.solicitante_negocio_id,
            receptor_negocio_id=rec.receptor_negocio_id,
            estado=AlianzaEstado(rec.estado),
            motivo=rec.motivo,
            fecha_solicitud=rec.fecha_solicitud,
            fecha_respuesta=rec.fecha_respuesta,
        )

    # ---- CRUD básico ----
    def get_by_id(self, id_: int) -> Optional[AlianzaData]:
        try:
            rec = AlianzaModel.get(AlianzaModel.id == id_)
            return self._to_entity(rec)
        except AlianzaModel.DoesNotExist:
            return None

    def get_all(self) -> List[AlianzaData]:
        return [self._to_entity(r) for r in AlianzaModel.select()]

    def create(self, a: AlianzaData) -> AlianzaData:
        rec = AlianzaModel.create(
            solicitante_negocio_id=a.solicitante_negocio_id,
            receptor_negocio_id=a.receptor_negocio_id,
            estado=(a.estado.value if isinstance(a.estado, AlianzaEstado) else str(a.estado)),
            motivo=a.motivo,
            fecha_solicitud=a.fecha_solicitud,
            fecha_respuesta=a.fecha_respuesta,
        )
        return self._to_entity(rec)

    def update(self, a: AlianzaData) -> Optional[AlianzaData]:
        try:
            rec = AlianzaModel.get(AlianzaModel.id == a.id)
            rec.solicitante_negocio_id = a.solicitante_negocio_id
            rec.receptor_negocio_id    = a.receptor_negocio_id
            rec.estado                 = a.estado.value if isinstance(a.estado, AlianzaEstado) else str(a.estado)
            rec.motivo                 = a.motivo
            rec.fecha_solicitud        = a.fecha_solicitud
            rec.fecha_respuesta        = a.fecha_respuesta
            rec.save()
            return self._to_entity(rec)
        except AlianzaModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = AlianzaModel.get(AlianzaModel.id == id_)
            rec.delete_instance()
            return True
        except AlianzaModel.DoesNotExist:
            return False

    # ---- Consultas útiles ----
    def find_by_negocio(self, negocio_id: int) -> List[AlianzaData]:
        q = (AlianzaModel
             .select()
             .where(
                 (AlianzaModel.solicitante_negocio_id == negocio_id) |
                 (AlianzaModel.receptor_negocio_id == negocio_id)
             ))
        return [self._to_entity(r) for r in q]

    def find_pendientes_recibidas(self, negocio_id: int) -> List[AlianzaData]:
        q = (AlianzaModel
             .select()
             .where(
                 (AlianzaModel.receptor_negocio_id == negocio_id) &
                 (AlianzaModel.estado == AlianzaEstado.PENDIENTE.value)
             ))
        return [self._to_entity(r) for r in q]

    def find_pendientes_enviadas(self, negocio_id: int) -> List[AlianzaData]:
        q = (AlianzaModel
             .select()
             .where(
                 (AlianzaModel.solicitante_negocio_id == negocio_id) &
                 (AlianzaModel.estado == AlianzaEstado.PENDIENTE.value)
             ))
        return [self._to_entity(r) for r in q]

    def find_activas(self, negocio_id: int) -> List[AlianzaData]:
        q = (AlianzaModel
             .select()
             .where(
                 ((AlianzaModel.solicitante_negocio_id == negocio_id) |
                  (AlianzaModel.receptor_negocio_id == negocio_id)) &
                 (AlianzaModel.estado == AlianzaEstado.ACEPTADA.value)
             ))
        return [self._to_entity(r) for r in q]

    def exists_between(self, negocio_a: int, negocio_b: int) -> Optional[AlianzaData]:
        q = (AlianzaModel
             .select()
             .where(
                 ((AlianzaModel.solicitante_negocio_id == negocio_a) &
                  (AlianzaModel.receptor_negocio_id == negocio_b)) |
                 ((AlianzaModel.solicitante_negocio_id == negocio_b) &
                  (AlianzaModel.receptor_negocio_id == negocio_a))
             )
             .limit(1))
        rec = q.first()
        return self._to_entity(rec) if rec else None

    def change_estado(self, id_: int, nuevo_estado: AlianzaEstado, motivo: str | None = None) -> Optional[AlianzaData]:
        try:
            rec = AlianzaModel.get(AlianzaModel.id == id_)
            rec.estado = nuevo_estado.value
            if motivo is not None:
                rec.motivo = motivo
            rec.fecha_respuesta = datetime.utcnow()
            rec.save()
            return self._to_entity(rec)
        except AlianzaModel.DoesNotExist:
            return None
