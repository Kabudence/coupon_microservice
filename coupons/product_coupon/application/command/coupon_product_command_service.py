from typing import List

from coupons.product_coupon.domain.entities.coupon_product import CouponProductData
from coupons.product_coupon.infraestructure.repositories.coupon_product_repository import CouponProductRepository


class CouponProductCommandService:
    def __init__(self, repo: CouponProductRepository):
        self.repo = repo

    def add_mapping(self, coupon_id: int, product_id: int) -> CouponProductData:
        entity = CouponProductData(coupon_id=coupon_id, product_id=product_id)
        return self.repo.add(entity)

    def bulk_add_mappings(self, coupon_id: int, product_ids: List[int]) -> List[CouponProductData]:
        if not product_ids:
            return []
        return self.repo.bulk_add(coupon_id, product_ids)

    def remove_mapping(self, coupon_id: int, product_id: int) -> bool:
        return self.repo.remove(coupon_id, product_id)

    def remove_all_for_coupon(self, coupon_id: int) -> int:
        return self.repo.remove_all_for_coupon(coupon_id)
