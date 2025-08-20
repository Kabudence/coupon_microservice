from enum import Enum
from typing import Optional


class ProductType(Enum):
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"


class CouponProductStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class CouponProductData:
    """
    Join entity for Coupon <-> Product mapping.
    Incluye:
      - code (obligatorio, str)
      - product_type (PRODUCT|SERVICE)
      - stock (opcional, >=0)
      - status (ACTIVE/INACTIVE)
    """
    def __init__(
        self,
        coupon_id: int,
        product_id: int,
        code: str,
        product_type: ProductType | str,
        stock: Optional[int] = None,
        status: CouponProductStatus | str = CouponProductStatus.ACTIVE,
    ):
        if coupon_id is None:
            raise ValueError("coupon_id is required")
        if product_id is None:
            raise ValueError("product_id is required")
        if code is None or str(code).strip() == "":
            raise ValueError("code is required")
        if product_type is None:
            raise ValueError("product_type is required")
        if stock is not None and int(stock) < 0:
            raise ValueError("stock must be >= 0")

        self.coupon_id = int(coupon_id)
        self.product_id = int(product_id)
        self.code = str(code).strip()
        self.product_type = product_type if isinstance(product_type, ProductType) else ProductType(str(product_type))
        self.stock = int(stock) if stock is not None else None
        self.status = status if isinstance(status, CouponProductStatus) else CouponProductStatus(str(status))

    def to_dict(self):
        return {
            "coupon_id": self.coupon_id,
            "product_id": self.product_id,
            "code": self.code,
            "product_type": self.product_type.value if isinstance(self.product_type, ProductType) else str(self.product_type),
            "stock": self.stock,
            "status": self.status.value if isinstance(self.status, CouponProductStatus) else str(self.status),
        }
