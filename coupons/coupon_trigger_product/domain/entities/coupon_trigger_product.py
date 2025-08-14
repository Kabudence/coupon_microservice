from decimal import Decimal
from typing import Optional


class CouponTriggerProductData:
    """
    Mapping that defines: buying product_trigger_id grants coupon_id,
    optionally constrained by min_quantity and/or min_amount.
    """
    def __init__(
        self,
        product_trigger_id: int,
        coupon_id: int,
        min_quantity: int = 1,
        min_amount: Optional[Decimal | float | str] = None,
    ):
        if product_trigger_id is None:
            raise ValueError("product_trigger_id is required")
        if coupon_id is None:
            raise ValueError("coupon_id is required")
        if min_quantity is None or int(min_quantity) < 1:
            raise ValueError("min_quantity must be >= 1")

        self.product_trigger_id = int(product_trigger_id)
        self.coupon_id = int(coupon_id)
        self.min_quantity = int(min_quantity)
        self.min_amount = (Decimal(str(min_amount)) if min_amount is not None else None)

    def to_dict(self):
        return {
            "product_trigger_id": self.product_trigger_id,
            "coupon_id": self.coupon_id,
            "min_quantity": self.min_quantity,
            "min_amount": (str(self.min_amount) if self.min_amount is not None else None),
        }
