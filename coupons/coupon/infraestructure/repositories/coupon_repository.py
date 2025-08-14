from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from coupons.coupon.domain.entities.coupon import CouponData, CouponStatus
from coupons.coupon.infraestructure.model.coupon_model import CouponModel


class CouponRepository:
    def _to_entity(self, rec: CouponModel) -> CouponData:
        return CouponData(
            id=rec.id,
            business_id=rec.business_id,
            coupon_type_id=(rec.coupon_type.id if rec.coupon_type is not None else None),
            name=rec.name,
            description=rec.description,
            discount_type_id=rec.discount_type.id,
            value=Decimal(str(rec.value)),
            max_discount=(Decimal(str(rec.max_discount)) if rec.max_discount is not None else None),
            start_date=rec.start_date,
            end_date=rec.end_date,
            max_uses=rec.max_uses,
            code=rec.code,
            event_name=rec.event_name,
            is_shared_alliances=bool(rec.is_shared_alliances),
            status=CouponStatus(rec.status),
            created_at=rec.created_at,
        )

    def get_by_id(self, id_: int) -> Optional[CouponData]:
        try:
            rec = CouponModel.get(CouponModel.id == id_)
            return self._to_entity(rec)
        except CouponModel.DoesNotExist:
            return None

    def get_all(self) -> List[CouponData]:
        return [self._to_entity(rec) for rec in CouponModel.select()]

    def find_active_in_window(self, now: datetime) -> List[CouponData]:
        q = (CouponModel
             .select()
             .where(
                 (CouponModel.status == CouponStatus.ACTIVE.value) &
                 (CouponModel.start_date <= now) &
                 (CouponModel.end_date >= now)
             ))
        return [self._to_entity(rec) for rec in q]

    def create(self, coupon: CouponData) -> CouponData:
        rec = CouponModel.create(
            business_id=coupon.business_id,
            coupon_type=coupon.coupon_type_id,
            name=coupon.name,
            description=coupon.description,
            discount_type=coupon.discount_type_id,
            value=str(coupon.value),
            max_discount=(str(coupon.max_discount) if coupon.max_discount is not None else None),
            start_date=coupon.start_date,
            end_date=coupon.end_date,
            max_uses=coupon.max_uses,
            code=coupon.code,
            event_name=coupon.event_name,
            is_shared_alliances=coupon.is_shared_alliances,
            status=coupon.status.value if isinstance(coupon.status, CouponStatus) else str(coupon.status),
        )
        return self._to_entity(rec)

    def update(self, coupon: CouponData) -> Optional[CouponData]:
        try:
            rec = CouponModel.get(CouponModel.id == coupon.id)
            rec.business_id = coupon.business_id
            rec.coupon_type = coupon.coupon_type_id
            rec.name = coupon.name
            rec.description = coupon.description
            rec.discount_type = coupon.discount_type_id
            rec.value = str(coupon.value)
            rec.max_discount = (str(coupon.max_discount) if coupon.max_discount is not None else None)
            rec.start_date = coupon.start_date
            rec.end_date = coupon.end_date
            rec.max_uses = coupon.max_uses
            rec.code = coupon.code
            rec.event_name = coupon.event_name
            rec.is_shared_alliances = coupon.is_shared_alliances
            rec.status = coupon.status.value if isinstance(coupon.status, CouponStatus) else str(coupon.status)
            rec.save()
            return self._to_entity(rec)
        except CouponModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = CouponModel.get(CouponModel.id == id_)
            rec.delete_instance()
            return True
        except CouponModel.DoesNotExist:
            return False

    def find_by_code(self, code: str) -> Optional[CouponData]:
        if not code:
            return None
        try:
            rec = CouponModel.get(CouponModel.code == code.strip())
            return self._to_entity(rec)
        except CouponModel.DoesNotExist:
            return None

    def find_by_business(self, business_id: int) -> List[CouponData]:
        q = CouponModel.select().where(CouponModel.business_id == business_id)
        return [self._to_entity(rec) for rec in q]
