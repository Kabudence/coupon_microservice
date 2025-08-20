from typing import List, Optional
from decimal import Decimal

from coupons.coupon_trigger_product.domain.entities.coupon_trigger_product import (
    CouponTriggerProductData, ProductType
)
from coupons.coupon_trigger_product.infraestructure.repositories.coupon_trigger_product_repository import \
    CouponTriggerProductRepository


class CouponTriggerProductCommandService:
    def __init__(self, repo: CouponTriggerProductRepository):
        self.repo = repo

    def add_mapping(
        self,
        product_trigger_id: int,
        coupon_id: int,
        product_type: ProductType | str,                 # <-- NUEVO
        min_quantity: int = 1,
        min_amount: Optional[Decimal | float | str] = None,
    ) -> CouponTriggerProductData:
        entity = CouponTriggerProductData(
            product_trigger_id=product_trigger_id,
            coupon_id=coupon_id,
            product_type=product_type,                    # <-- NUEVO
            min_quantity=min_quantity,
            min_amount=min_amount,
        )
        return self.repo.add(entity)

    def bulk_add_mappings(
        self,
        coupon_id: int,
        product_trigger_ids: List[int],
        product_type: ProductType | str = "PRODUCT",      # <-- NUEVO
        min_quantity: int = 1,
        min_amount: Optional[Decimal | float | str] = None,
    ) -> List[CouponTriggerProductData]:
        return self.repo.bulk_add(coupon_id, product_trigger_ids, product_type, min_quantity, min_amount)

    def remove_mapping(self, product_trigger_id: int, coupon_id: int) -> bool:
        return self.repo.remove(product_trigger_id, coupon_id)

    def remove_all_for_coupon(self, coupon_id: int) -> int:
        return self.repo.remove_all_for_coupon(coupon_id)
