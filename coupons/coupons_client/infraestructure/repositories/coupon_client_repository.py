from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from coupons.coupon_client.domain.entities.coupon_client import (
    CouponClientData, CouponClientStatus
)
from coupons.coupon_client.infraestructure.model.coupon_client_model import CouponClientModel


class CouponClientRepository:
    def _to_entity(self, rec: CouponClientModel) -> CouponClientData:
        return CouponClientData(
            id=rec.id,
            coupon_id=rec.coupon_id,
            client_id=rec.client_id,
            code=rec.code,
            status=CouponClientStatus(rec.status),
            valid_from=rec.valid_from,
            valid_to=rec.valid_to,
            used_at=rec.used_at,
            source_trigger_id=rec.source_trigger_id,
            source_order_id=rec.source_order_id,
            created_at=rec.created_at,
        )

    def create(self, cc: CouponClientData) -> CouponClientData:
        rec = CouponClientModel.create(
            coupon_id=cc.coupon_id,
            client_id=cc.client_id,
            code=cc.code,
            status=cc.status.value if isinstance(cc.status, CouponClientStatus) else str(cc.status),
            valid_from=cc.valid_from,
            valid_to=cc.valid_to,
            used_at=cc.used_at,
            source_trigger_id=cc.source_trigger_id,
            source_order_id=cc.source_order_id,
        )
        return self._to_entity(rec)

    def get_by_id(self, id_: int) -> Optional[CouponClientData]:
        try:
            rec = CouponClientModel.get(CouponClientModel.id == id_)
            return self._to_entity(rec)
        except CouponClientModel.DoesNotExist:
            return None

    def list_by_client(self, client_id: int) -> List[CouponClientData]:
        q = CouponClientModel.select().where(CouponClientModel.client_id == client_id)
        return [self._to_entity(r) for r in q]

    def list_active_for_client(self, client_id: int, now: Optional[datetime] = None) -> List[CouponClientData]:
        now = now or datetime.utcnow()
        q = (CouponClientModel
             .select()
             .where(
                 (CouponClientModel.client_id == client_id) &
                 (CouponClientModel.status == CouponClientStatus.ACTIVE.value) &
                 ((CouponClientModel.valid_from >> None) | (CouponClientModel.valid_from <= now)) &
                 ((CouponClientModel.valid_to >> None)   | (CouponClientModel.valid_to >= now))
             ))
        return [self._to_entity(r) for r in q]

    def mark_used(self, id_: int, order_id: Optional[int] = None) -> Optional[CouponClientData]:
        try:
            rec = CouponClientModel.get(CouponClientModel.id == id_)
            rec.status = CouponClientStatus.USED.value
            rec.used_at = datetime.utcnow()
            if order_id:
                rec.source_order_id = order_id
            rec.save()
            return self._to_entity(rec)
        except CouponClientModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = CouponClientModel.get(CouponClientModel.id == id_)
            rec.delete_instance()
            return True
        except CouponClientModel.DoesNotExist:
            return False
