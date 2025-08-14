from typing import List, Optional

from coupons.coupons_type.domain.entities.coupon_type import CouponTypeData
from coupons.coupons_type.infraestructure.repositories.coupon_type_repository import CouponTypeRepository


class CouponTypeQueryService:
    def __init__(self, repo: CouponTypeRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[CouponTypeData]:
        return self.repo.get_by_id(id_)

    def list_all(self) -> List[CouponTypeData]:
        return self.repo.get_all()

    def find_by_name(self, name: Optional[str] = None) -> List[CouponTypeData]:
        return self.repo.find_by_name(name)
