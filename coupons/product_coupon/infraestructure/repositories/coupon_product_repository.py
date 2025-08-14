from typing import List

from coupons.product_coupon.domain.entities.coupon_product import CouponProductData
from coupons.product_coupon.infraestructure.model.coupon_product_model import CouponProductModel


class CouponProductRepository:
    def add(self, entity: CouponProductData) -> CouponProductData:
        # Upsert-like: ignore duplicates via try/except
        try:
            CouponProductModel.create(
                coupon=entity.coupon_id,
                product_id=entity.product_id
            )
        except Exception:
            # If composite PK already exists, we simply return the entity
            pass
        return entity

    def bulk_add(self, coupon_id: int, product_ids: List[int]) -> List[CouponProductData]:
        created: List[CouponProductData] = []
        with CouponProductModel._meta.database.atomic():
            for pid in product_ids:
                try:
                    CouponProductModel.create(coupon=coupon_id, product_id=pid)
                    created.append(CouponProductData(coupon_id=coupon_id, product_id=pid))
                except Exception:
                    # ignore duplicates
                    pass
        return created

    def remove(self, coupon_id: int, product_id: int) -> bool:
        deleted = (CouponProductModel
                   .delete()
                   .where((CouponProductModel.coupon == coupon_id) &
                          (CouponProductModel.product_id == product_id))
                   .execute())
        return deleted > 0

    def remove_all_for_coupon(self, coupon_id: int) -> int:
        return (CouponProductModel
                .delete()
                .where(CouponProductModel.coupon == coupon_id)
                .execute())

    def list_products_by_coupon(self, coupon_id: int) -> List[int]:
        return [rec.product_id
                for rec in CouponProductModel
                .select(CouponProductModel.product_id)
                .where(CouponProductModel.coupon == coupon_id)]

    def list_coupons_by_product(self, product_id: int) -> List[int]:
        return [rec.coupon.id
                for rec in CouponProductModel
                .select(CouponProductModel.coupon)
                .where(CouponProductModel.product_id == product_id)]
