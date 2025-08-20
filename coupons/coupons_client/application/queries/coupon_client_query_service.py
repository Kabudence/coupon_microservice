from datetime import datetime
from typing import Optional, List

from coupons.coupons_client.domain.entities.cupon_client import CouponClientData
from coupons.coupons_client.infraestructure.repositories.coupon_client_repository import CouponClientRepository


class CouponClientQueryService:
    def __init__(self, repo: CouponClientRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[CouponClientData]:
        return self.repo.get_by_id(id_)

    def list_by_client(self, client_id: int) -> List[CouponClientData]:
        return self.repo.list_by_client(client_id)

    def list_active_for_client(self, client_id: int, now: Optional[datetime] = None) -> List[CouponClientData]:
        return self.repo.list_active_for_client(client_id, now)