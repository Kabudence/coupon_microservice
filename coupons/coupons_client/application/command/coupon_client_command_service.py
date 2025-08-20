from __future__ import annotations
from datetime import datetime
from typing import Optional

from coupons.coupons_client.domain.entities.cupon_client import CouponClientData, CouponClientStatus
from coupons.coupons_client.infraestructure.repositories.coupon_client_repository import CouponClientRepository




class CouponClientCommandService:
    def __init__(self, repo: CouponClientRepository):
        self.repo = repo

    def assign_to_client(
        self,
        coupon_id: int,
        client_id: int,
        code: str,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        source_trigger_id: Optional[int] = None,
        source_order_id: Optional[int] = None,
        status: CouponClientStatus = CouponClientStatus.ACTIVE
    ) -> CouponClientData:
        entity = CouponClientData(
            coupon_id=coupon_id,
            client_id=client_id,
            code=code,
            status=status,
            valid_from=valid_from,
            valid_to=valid_to,
            source_trigger_id=source_trigger_id,
            source_order_id=source_order_id
        )
        return self.repo.create(entity)

    def mark_used(self, id_: int, order_id: Optional[int] = None) -> Optional[CouponClientData]:
        return self.repo.mark_used(id_, order_id)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)



