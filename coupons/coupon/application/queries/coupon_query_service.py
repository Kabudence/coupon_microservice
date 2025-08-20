from typing import List, Optional
from datetime import datetime

from coupons.coupon.domain.entities.coupon import CouponData
from coupons.coupon.infraestructure.repositories.coupon_repository import CouponRepository


class CouponQueryService:
    def __init__(self, repo: CouponRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[CouponData]:
        return self.repo.get_by_id(id_)

    def list_all(self) -> List[CouponData]:
        return self.repo.get_all()

    def find_by_business(self, business_id: int) -> List[CouponData]:
        return self.repo.find_by_business(business_id)

    def list_active_in_window(self, now: datetime) -> List[CouponData]:
        return self.repo.find_active_in_window(now)
