from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Optional


class CouponStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class CouponData:
    def __init__(
        self,
        id: int = None,
        business_id: int = None,
        coupon_type_id: Optional[int] = None,
        name: str = "",
        description: Optional[str] = None,
        discount_type_id: int = None,              # PERCENTAGE / AMOUNT (FK -> discount_type)
        value: Decimal | float | str = 0,          # % or amount (according to discount_type)
        max_discount: Optional[Decimal | float | str] = None,  # hard cap to applied discount
        start_date: datetime = None,
        end_date: datetime = None,
        max_uses: Optional[int] = None,            # global limit across the system
        code: Optional[str] = None,
        event_name: Optional[str] = None,
        is_shared_alliances: bool = False,
        status: CouponStatus = CouponStatus.ACTIVE,
        created_at: Optional[datetime] = None,
    ):
        # Required validations
        if business_id is None:
            raise ValueError("business_id is required")
        if name is None or str(name).strip() == "":
            raise ValueError("name cannot be None or empty")
        if discount_type_id is None:
            raise ValueError("discount_type_id is required")
        if start_date is None or end_date is None:
            raise ValueError("start_date and end_date are required")
        if end_date <= start_date:
            raise ValueError("end_date must be greater than start_date")
        if status is None:
            raise ValueError("status is required")

        # Basic fields
        self.id = id
        self.business_id = business_id
        self.coupon_type_id = coupon_type_id
        self.name = str(name).strip()
        self.description = (str(description).strip() if description else None)

        # Numeric fields
        self.discount_type_id = discount_type_id
        self.value = Decimal(str(value))
        if self.value < 0:
            raise ValueError("value must be >= 0")

        self.max_discount = Decimal(str(max_discount)) if max_discount is not None else None
        if self.max_discount is not None and self.max_discount < 0:
            raise ValueError("max_discount must be >= 0")

        # Dates
        self.start_date = start_date
        self.end_date = end_date

        # Optional
        self.max_uses = max_uses
        self.code = str(code).strip() if code else None
        self.event_name = str(event_name).strip() if event_name else None
        self.is_shared_alliances = bool(is_shared_alliances)

        # Enum normalize
        self.status = status if isinstance(status, CouponStatus) else CouponStatus(str(status))

        # Server set
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "business_id": self.business_id,
            "coupon_type_id": self.coupon_type_id,
            "name": self.name,
            "description": self.description,
            "discount_type_id": self.discount_type_id,
            "value": str(self.value),
            "max_discount": (str(self.max_discount) if self.max_discount is not None else None),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "max_uses": self.max_uses,
            "code": self.code,
            "event_name": self.event_name,
            "is_shared_alliances": self.is_shared_alliances,
            "status": self.status.value if isinstance(self.status, CouponStatus) else self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
