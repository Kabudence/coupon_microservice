from typing import Optional, List
from decimal import Decimal

from coupons.coupon_segment_price.domain.entities.coupon_segment_price import CouponSegmentPriceData
from coupons.coupon_segment_price.infraestructure.model.coupon_segment_price_model import CouponSegmentPriceModel


class CouponSegmentPriceRepository:
    def _to_entity(self, rec: CouponSegmentPriceModel) -> CouponSegmentPriceData:
        return CouponSegmentPriceData(
            coupon_id=rec.coupon.id,
            segment_id=rec.segment.id,
            discount_type_id=rec.discount_type.id,
            value=Decimal(str(rec.value)),
            priority=rec.priority,
        )

    def get(self, coupon_id: int, segment_id: int) -> Optional[CouponSegmentPriceData]:
        try:
            rec = (CouponSegmentPriceModel
                   .get(
                        (CouponSegmentPriceModel.coupon == coupon_id) &
                        (CouponSegmentPriceModel.segment == segment_id)
                   ))
            return self._to_entity(rec)
        except CouponSegmentPriceModel.DoesNotExist:
            return None

    def list_by_coupon(self, coupon_id: int) -> List[CouponSegmentPriceData]:
        q = (CouponSegmentPriceModel
             .select()
             .where(CouponSegmentPriceModel.coupon == coupon_id)
             .order_by(CouponSegmentPriceModel.priority.asc()))
        return [self._to_entity(rec) for rec in q]

    def list_by_segment(self, segment_id: int) -> List[CouponSegmentPriceData]:
        q = (CouponSegmentPriceModel
             .select()
             .where(CouponSegmentPriceModel.segment == segment_id))
        return [self._to_entity(rec) for rec in q]

    def create(self, entity: CouponSegmentPriceData) -> CouponSegmentPriceData:
        CouponSegmentPriceModel.create(
            coupon=entity.coupon_id,
            segment=entity.segment_id,
            discount_type=entity.discount_type_id,
            value=str(entity.value),
            priority=entity.priority,
        )
        # Composite PK guarantees uniqueness; return what was inserted
        return entity

    def upsert(self, entity: CouponSegmentPriceData) -> CouponSegmentPriceData:
        """Create or update the (coupon_id, segment_id) row."""
        rec, created = CouponSegmentPriceModel.get_or_create(
            coupon=entity.coupon_id,
            segment=entity.segment_id,
            defaults={
                'discount_type': entity.discount_type_id,
                'value': str(entity.value),
                'priority': entity.priority
            }
        )
        if not created:
            rec.discount_type = entity.discount_type_id
            rec.value = str(entity.value)
            rec.priority = entity.priority
            rec.save()
        return self._to_entity(rec)

    def update(self, entity: CouponSegmentPriceData) -> Optional[CouponSegmentPriceData]:
        try:
            rec = (CouponSegmentPriceModel
                   .get(
                        (CouponSegmentPriceModel.coupon == entity.coupon_id) &
                        (CouponSegmentPriceModel.segment == entity.segment_id)
                   ))
            rec.discount_type = entity.discount_type_id
            rec.value = str(entity.value)
            rec.priority = entity.priority
            rec.save()
            return self._to_entity(rec)
        except CouponSegmentPriceModel.DoesNotExist:
            return None

    def delete(self, coupon_id: int, segment_id: int) -> bool:
        deleted = (CouponSegmentPriceModel
                   .delete()
                   .where(
                       (CouponSegmentPriceModel.coupon == coupon_id) &
                       (CouponSegmentPriceModel.segment == segment_id)
                   ).execute())
        return deleted > 0

    def delete_all_for_coupon(self, coupon_id: int) -> int:
        return (CouponSegmentPriceModel
                .delete()
                .where(CouponSegmentPriceModel.coupon == coupon_id)
                .execute())

    def count_for_coupon(self, coupon_id: int) -> int:
        return (CouponSegmentPriceModel
                .select()
                .where(CouponSegmentPriceModel.coupon == coupon_id)
                .count())
