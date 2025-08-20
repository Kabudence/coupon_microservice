# coupons/product_coupon/application/coupon_product_command_service.py
from typing import List, Dict, Optional

from coupons.product_coupon.domain.entities.coupon_product import (
    CouponProductData, ProductType, CouponProductStatus
)
from coupons.product_coupon.infraestructure.repositories.coupon_product_repository import CouponProductRepository


class CouponProductCommandService:
    def __init__(self, repo: CouponProductRepository):
        self.repo = repo

    def add_mapping(
        self,
        coupon_id: int,
        product_id: int,
        code: str,
        product_type: ProductType | str,
        stock: int | None = None,
        status: CouponProductStatus | str = CouponProductStatus.ACTIVE,
    ) -> CouponProductData:
        entity = CouponProductData(
            coupon_id=coupon_id,
            product_id=product_id,
            code=code,
            product_type=product_type,
            stock=stock,
            status=status,
        )
        return self.repo.add(entity)

    def bulk_add_mappings(self, coupon_id: int, items: List[Dict]) -> List[CouponProductData]:
        """
        items = [
          {"product_id": 111, "code": "SKU001", "product_type": "PRODUCT", "stock": 5, "status": "ACTIVE"},
          {"product_id": 222, "code": "SRV-02", "product_type": "SERVICE", "status": "INACTIVE"},
        ]
        """
        if not items:
            return []
        return self.repo.bulk_add(coupon_id, items)

    def remove_mapping(self, coupon_id: int, product_id: int) -> bool:
        """Compat: elimina por (coupon, product_id)."""
        return self.repo.remove(coupon_id, product_id)

    def remove_by_combo(
        self,
        coupon_id: int,
        product_id: int,
        code: Optional[str] = None,
        product_type: Optional[str] = None,
    ) -> int:
        """Elimina respetando code/product_type si se envían. Devuelve cantidad borrada."""
        return self.repo.remove_by_combo(coupon_id, product_id, code=code, product_type=product_type)

    def remove_all_for_coupon(self, coupon_id: int) -> int:
        return self.repo.remove_all_for_coupon(coupon_id)

    # ===== NUEVO: consumir 1 de stock =====
    def consume_one(
        self,
        coupon_id: int,
        product_id: int,
        code: Optional[str] = None,
        product_type: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Resta 1 al stock si aplica. Si llega a 0 => status INACTIVE.
        Si stock es NULL (sin control), no cambia stock/status.
        Devuelve dict resumen o None si no existe el mapping.
        """
        return self.repo.consume_one(coupon_id, product_id, code=code, product_type=product_type)
