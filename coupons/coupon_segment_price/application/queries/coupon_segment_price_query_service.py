from typing import List, Optional

from coupons.coupon_segment_price.domain.entities.coupon_segment_price import CouponSegmentPriceData
from coupons.coupon_segment_price.infraestructure.repositories.coupon_segment_price_repository import \
    CouponSegmentPriceRepository


class CouponSegmentPriceQueryService:
    def __init__(self, repo: CouponSegmentPriceRepository):
        self.repo = repo

    def get(self, coupon_id: int, segment_id: int) -> Optional[CouponSegmentPriceData]:
        return self.repo.get(coupon_id, segment_id)

    def list_by_coupon(self, coupon_id: int) -> List[CouponSegmentPriceData]:
        return self.repo.list_by_coupon(coupon_id)

    def list_by_segment(self, segment_id: int) -> List[CouponSegmentPriceData]:
        return self.repo.list_by_segment(segment_id)
