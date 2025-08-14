from typing import List

from coupons.coupon_trigger_product.domain.entities.coupon_trigger_product import CouponTriggerProductData
from coupons.coupon_trigger_product.infraestructure.model.coupon_trigger_product_model import CouponTriggerProductModel


class CouponTriggerProductRepository:
    def add(self, entity: CouponTriggerProductData) -> CouponTriggerProductData:
        try:
            CouponTriggerProductModel.create(
                product_trigger_id=entity.product_trigger_id,
                coupon=entity.coupon_id,
                min_quantity=entity.min_quantity,
                min_amount=(str(entity.min_amount) if entity.min_amount is not None else None),
            )
        except Exception:
            # composite PK duplicate -> ignore (idempotent upsert-like)
            pass
        return entity

    def bulk_add(self, coupon_id: int, product_trigger_ids: List[int], min_quantity: int = 1, min_amount=None) -> List[CouponTriggerProductData]:
        created: List[CouponTriggerProductData] = []
        if not product_trigger_ids:
            return created
        with CouponTriggerProductModel._meta.database.atomic():
            for pid in product_trigger_ids:
                try:
                    CouponTriggerProductModel.create(
                        product_trigger_id=pid,
                        coupon=coupon_id,
                        min_quantity=min_quantity,
                        min_amount=(str(min_amount) if min_amount is not None else None),
                    )
                    created.append(
                        CouponTriggerProductData(
                            product_trigger_id=pid,
                            coupon_id=coupon_id,
                            min_quantity=min_quantity,
                            min_amount=min_amount,
                        )
                    )
                except Exception:
                    # ignore duplicates
                    pass
        return created

    def remove(self, product_trigger_id: int, coupon_id: int) -> bool:
        deleted = (CouponTriggerProductModel
                   .delete()
                   .where(
                       (CouponTriggerProductModel.product_trigger_id == product_trigger_id) &
                       (CouponTriggerProductModel.coupon == coupon_id)
                   ).execute())
        return deleted > 0

    def remove_all_for_coupon(self, coupon_id: int) -> int:
        return (CouponTriggerProductModel
                .delete()
                .where(CouponTriggerProductModel.coupon == coupon_id)
                .execute())

    def list_triggers_by_coupon(self, coupon_id: int) -> List[CouponTriggerProductData]:
        q = (CouponTriggerProductModel
             .select()
             .where(CouponTriggerProductModel.coupon == coupon_id))
        return [
            CouponTriggerProductData(
                product_trigger_id=rec.product_trigger_id,
                coupon_id=rec.coupon.id,
                min_quantity=rec.min_quantity,
                min_amount=rec.min_amount,
            )
            for rec in q
        ]

    def list_coupons_by_trigger(self, product_trigger_id: int) -> List[int]:
        q = (CouponTriggerProductModel
             .select(CouponTriggerProductModel.coupon)
             .where(CouponTriggerProductModel.product_trigger_id == product_trigger_id))
        return [rec.coupon.id for rec in q]
