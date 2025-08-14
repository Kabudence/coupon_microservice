from typing import List

from coupons.product_coupon.infraestructure.repositories.coupon_product_repository import CouponProductRepository


class CouponProductQueryService:
    def __init__(self, repo: CouponProductRepository):
        self.repo = repo

    def list_products_by_coupon(self, coupon_id: int) -> List[int]:
        return self.repo.list_products_by_coupon(coupon_id)

    def list_coupons_by_product(self, product_id: int) -> List[int]:
        return self.repo.list_coupons_by_product(product_id)
