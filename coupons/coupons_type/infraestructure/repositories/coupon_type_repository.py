from typing import Optional, List

from coupons.coupons_type.domain.entities.coupon_type import CouponTypeData
from coupons.coupons_type.infraestructure.model.coupon_type_model import CouponTypeModel


class CouponTypeRepository:
    def get_by_id(self, id_: int) -> Optional[CouponTypeData]:
        try:
            rec = CouponTypeModel.get(CouponTypeModel.id == id_)
            return CouponTypeData(id=rec.id, name=rec.name, description=rec.description)
        except CouponTypeModel.DoesNotExist:
            return None

    def get_all(self) -> List[CouponTypeData]:
        return [
            CouponTypeData(id=rec.id, name=rec.name, description=rec.description)
            for rec in CouponTypeModel.select()
        ]

    def find_by_name(self, name: str) -> List[CouponTypeData]:
        if not name:
            return []
        q = CouponTypeModel.select().where(CouponTypeModel.name == name.strip())
        return [
            CouponTypeData(id=rec.id, name=rec.name, description=rec.description)
            for rec in q
        ]

    def create(self, coupon_type: CouponTypeData) -> CouponTypeData:
        rec = CouponTypeModel.create(
            name=coupon_type.name,
            description=coupon_type.description
        )
        return CouponTypeData(id=rec.id, name=rec.name, description=rec.description)

    def update(self, coupon_type: CouponTypeData) -> Optional[CouponTypeData]:
        try:
            rec = CouponTypeModel.get(CouponTypeModel.id == coupon_type.id)
            rec.name = coupon_type.name
            rec.description = coupon_type.description
            rec.save()
            return CouponTypeData(id=rec.id, name=rec.name, description=rec.description)
        except CouponTypeModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = CouponTypeModel.get(CouponTypeModel.id == id_)
            rec.delete_instance()
            return True
        except CouponTypeModel.DoesNotExist:
            return False
