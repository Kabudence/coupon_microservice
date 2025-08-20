from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import Optional


class CouponClientStatus(Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class CouponClientData:
    def __init__(
        self,
        id: Optional[int] = None,
        coupon_id: int = None,
        client_id: int = None,
        code: str = "",
        status: CouponClientStatus | str = CouponClientStatus.ACTIVE,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        used_at: Optional[datetime] = None,
        source_trigger_id: Optional[int] = None,
        source_order_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ):
        if coupon_id is None:
            raise ValueError("coupon_id is required")
        if client_id is None:
            raise ValueError("client_id is required")
        if not code or str(code).strip() == "":
            raise ValueError("code is required")

        self.id = id
        self.coupon_id = int(coupon_id)
        self.client_id = int(client_id)
        self.code = str(code).strip()
        self.status = status if isinstance(status, CouponClientStatus) else CouponClientStatus(str(status))
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.used_at = used_at
        self.source_trigger_id = source_trigger_id
        self.source_order_id = source_order_id
        self.created_at = created_at

    def is_active_now(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.utcnow()
        if self.status != CouponClientStatus.ACTIVE:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "coupon_id": self.coupon_id,
            "client_id": self.client_id,
            "code": self.code,
            "status": self.status.value if isinstance(self.status, CouponClientStatus) else str(self.status),
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "source_trigger_id": self.source_trigger_id,
            "source_order_id": self.source_order_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
