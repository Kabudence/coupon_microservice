from typing import Optional


class CouponProductData:
    """
    Join entity for Coupon <-> Product mapping.
    """
    def __init__(self, coupon_id: int, product_id: int):
        if coupon_id is None:
            raise ValueError("coupon_id is required")
        if product_id is None:
            raise ValueError("product_id is required")

        self.coupon_id = int(coupon_id)
        self.product_id = int(product_id)

    def to_dict(self):
        return {
            "coupon_id": self.coupon_id,
            "product_id": self.product_id
        }
