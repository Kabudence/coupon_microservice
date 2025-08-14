from typing import Optional

from coupons.coupons_type.domain.entities.coupon_type import CouponTypeData
from coupons.coupons_type.infraestructure.repositories.coupon_type_repository import CouponTypeRepository


class CouponTypeCommandService:
    def __init__(self, repo: CouponTypeRepository):
        self.repo = repo

    def create(self, name: str, description: Optional[str] = None) -> CouponTypeData:
        if not name or str(name).strip() == "":
            raise ValueError("name is required")
        entity = CouponTypeData(name=name, description=description)
        return self.repo.create(entity)

    def update(self, id_: int, name: str, description: Optional[str] = None) -> Optional[CouponTypeData]:
        current = self.repo.get_by_id(id_)
        if not current:
            raise ValueError("CouponType not found.")
        current.name = name.strip()
        current.description = description.strip() if description else None
        return self.repo.update(current)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
