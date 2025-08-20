from typing import Optional
from datetime import datetime
from decimal import Decimal

from coupons.coupon.domain.entities.coupon import CouponStatus, CouponData
from coupons.coupon.infraestructure.repositories.coupon_repository import CouponRepository


class CouponCommandService:
    def __init__(self, repo: CouponRepository):
        self.repo = repo

    def create(
        self,
        business_id: int,
        name: str,
        discount_type_id: int,
        value: Decimal | float | str,
        start_date: datetime,
        end_date: datetime,
        coupon_type_id: Optional[int] = None,
        description: Optional[str] = None,
        max_discount: Optional[Decimal | float | str] = None,
        max_uses: Optional[int] = None,
        event_name: Optional[str] = None,
        is_shared_alliances: bool = False,
        status: CouponStatus = CouponStatus.ACTIVE,
        category_id: Optional[int] = None,
        event_id: Optional[int] = None,
        show_in_coupon_holder: bool = False,
    ) -> CouponData:
        entity = CouponData(
            business_id=business_id,
            coupon_type_id=coupon_type_id,
            category_id=category_id,
            event_id=event_id,
            show_in_coupon_holder=show_in_coupon_holder,
            name=name,
            description=description,
            discount_type_id=discount_type_id,
            value=value,
            max_discount=max_discount,
            start_date=start_date,
            end_date=end_date,
            max_uses=max_uses,
            event_name=event_name,
            is_shared_alliances=is_shared_alliances,
            status=status,
        )
        return self.repo.create(entity)

    def update(
        self,
        id_: int,
        business_id: int,
        name: str,
        discount_type_id: int,
        value: Decimal | float | str,
        start_date: datetime,
        end_date: datetime,
        coupon_type_id: Optional[int] = None,
        description: Optional[str] = None,
        max_discount: Optional[Decimal | float | str] = None,
        max_uses: Optional[int] = None,
        event_name: Optional[str] = None,
        is_shared_alliances: bool = False,
        status: CouponStatus = CouponStatus.ACTIVE,
        category_id: Optional[int] = None,
        event_id: Optional[int] = None,
        show_in_coupon_holder: bool = False,
    ) -> Optional[CouponData]:
        current = self.repo.get_by_id(id_)
        if not current:
            raise ValueError("Coupon not found.")

        current.business_id = business_id
        current.coupon_type_id = coupon_type_id
        current.category_id = category_id
        current.event_id = event_id
        current.show_in_coupon_holder = bool(show_in_coupon_holder)

        current.name = name
        current.description = description
        current.discount_type_id = discount_type_id
        current.value = Decimal(str(value))
        current.max_discount = (Decimal(str(max_discount)) if max_discount is not None else None)
        current.start_date = start_date
        current.end_date = end_date
        current.max_uses = max_uses
        current.event_name = event_name
        current.is_shared_alliances = bool(is_shared_alliances)
        current.status = status

        return self.repo.update(current)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
