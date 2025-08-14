from typing import Optional
from decimal import Decimal

from coupons.coupon_segment_price.domain.entities.coupon_segment_price import CouponSegmentPriceData
from coupons.coupon_segment_price.infraestructure.repositories.coupon_segment_price_repository import \
    CouponSegmentPriceRepository


class CouponSegmentPriceCommandService:
    def __init__(self, repo: CouponSegmentPriceRepository):
        self.repo = repo

    def create(
        self,
        coupon_id: int,
        segment_id: int,
        discount_type_id: int,
        value: Decimal | float | str,
        priority: int = 1,
        enforce_max_per_coupon: Optional[int] = None  # e.g., 2 if you want to cap per coupon
    ) -> CouponSegmentPriceData:
        if enforce_max_per_coupon is not None:
            current = self.repo.count_for_coupon(coupon_id)
            if current >= enforce_max_per_coupon:
                raise ValueError(f"Max segment overrides per coupon reached ({enforce_max_per_coupon}).")

        entity = CouponSegmentPriceData(
            coupon_id=coupon_id,
            segment_id=segment_id,
            discount_type_id=discount_type_id,
            value=value,
            priority=priority
        )
        return self.repo.create(entity)

    def upsert(
        self,
        coupon_id: int,
        segment_id: int,
        discount_type_id: int,
        value: Decimal | float | str,
        priority: int = 1
    ):
        entity = CouponSegmentPriceData(
            coupon_id=coupon_id,
            segment_id=segment_id,
            discount_type_id=discount_type_id,
            value=value,
            priority=priority
        )
        return self.repo.upsert(entity)

    def update(
        self,
        coupon_id: int,
        segment_id: int,
        discount_type_id: int,
        value: Decimal | float | str,
        priority: int = 1
    ):
        entity = CouponSegmentPriceData(
            coupon_id=coupon_id,
            segment_id=segment_id,
            discount_type_id=discount_type_id,
            value=value,
            priority=priority
        )
        updated = self.repo.update(entity)
        if not updated:
            raise ValueError("CouponSegmentPrice not found.")
        return updated

    def delete(self, coupon_id: int, segment_id: int) -> bool:
        return self.repo.delete(coupon_id, segment_id)

    def delete_all_for_coupon(self, coupon_id: int) -> int:
        return self.repo.delete_all_for_coupon(coupon_id)
