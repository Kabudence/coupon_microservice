from decimal import Decimal


class CouponSegmentPriceData:
    """
    Override for a coupon's discount when the customer matches a given segment.
    Composite PK: (coupon_id, segment_id)
    """
    def __init__(
        self,
        coupon_id: int,
        segment_id: int,
        discount_type_id: int,      # FK -> discount_type (PERCENTAGE/AMOUNT)
        value: Decimal | float | str,
        priority: int = 1           # 1 = highest priority
    ):
        if coupon_id is None:
            raise ValueError("coupon_id is required")
        if segment_id is None:
            raise ValueError("segment_id is required")
        if discount_type_id is None:
            raise ValueError("discount_type_id is required")
        if priority is None or int(priority) < 1:
            raise ValueError("priority must be >= 1")

        self.coupon_id = int(coupon_id)
        self.segment_id = int(segment_id)
        self.discount_type_id = int(discount_type_id)

        self.value = Decimal(str(value))
        if self.value < 0:
            raise ValueError("value must be >= 0")

        self.priority = int(priority)

    def to_dict(self):
        return {
            "coupon_id": self.coupon_id,
            "segment_id": self.segment_id,
            "discount_type_id": self.discount_type_id,
            "value": str(self.value),
            "priority": self.priority
        }
