from decimal import Decimal
from enum import Enum
from typing import Optional


class ProductType(Enum):
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"


class CouponTriggerProductData:
    """
    Comprar 'product_trigger_id' (PRODUCT o SERVICE) otorga 'coupon_id',
    con reglas opcionales de min_quantity y/o min_amount.
    """
    def __init__(
        self,
        product_trigger_id: int,
        coupon_id: int,
        product_type: ProductType | str,           # <-- NUEVO (obligatorio)
        min_quantity: int = 1,
        min_amount: Optional[Decimal | float | str] = None,
    ):
        if product_trigger_id is None:
            raise ValueError("product_trigger_id is required")
        if coupon_id is None:
            raise ValueError("coupon_id is required")
        if product_type is None:
            raise ValueError("product_type is required")
        if min_quantity is None or int(min_quantity) < 1:
            raise ValueError("min_quantity must be >= 1")

        self.product_trigger_id = int(product_trigger_id)
        self.coupon_id = int(coupon_id)
        self.product_type = (  # normaliza enum
            product_type if isinstance(product_type, ProductType)
            else ProductType(str(product_type))
        )
        self.min_quantity = int(min_quantity)
        self.min_amount = (Decimal(str(min_amount)) if min_amount is not None else None)

    def to_dict(self):
        return {
            "product_trigger_id": self.product_trigger_id,
            "coupon_id": self.coupon_id,
            "product_type": self.product_type.value,            # <-- NUEVO
            "min_quantity": self.min_quantity,
            "min_amount": (str(self.min_amount) if self.min_amount is not None else None),
        }
