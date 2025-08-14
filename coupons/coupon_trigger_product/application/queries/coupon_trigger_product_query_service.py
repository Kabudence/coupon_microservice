from typing import List

from coupons.coupon_trigger_product.domain.entities.coupon_trigger_product import CouponTriggerProductData
from coupons.coupon_trigger_product.infraestructure.repositories.coupon_trigger_product_repository import \
    CouponTriggerProductRepository


class CouponTriggerProductQueryService:
    def __init__(self, repo: CouponTriggerProductRepository):
        self.repo = repo

    def list_triggers_by_coupon(self, coupon_id: int) -> List[CouponTriggerProductData]:
        return self.repo.list_triggers_by_coupon(coupon_id)

    def list_coupons_by_trigger(self, product_trigger_id: int) -> List[int]:
        return self.repo.list_coupons_by_trigger(product_trigger_id)
