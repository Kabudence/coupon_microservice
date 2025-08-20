# coupons/product_coupon/infraestructure/repositories/coupon_product_repository.py
from __future__ import annotations
from typing import List, Dict, Optional

from peewee import fn

from coupons.product_coupon.domain.entities.coupon_product import (
    CouponProductData, ProductType, CouponProductStatus
)
from coupons.product_coupon.infraestructure.model.coupon_product_model import CouponProductModel


class CouponProductRepository:
    # ---------- Helpers ----------
    def _to_entity(self, rec: CouponProductModel) -> CouponProductData:
        return CouponProductData(
            coupon_id=rec.coupon_id if hasattr(rec, "coupon_id") else rec.coupon.id,
            product_id=rec.product_id,
            code=rec.code,
            product_type=ProductType(rec.product_type),
            stock=rec.stock,
            status=CouponProductStatus(rec.status),
        )

    def _find_one(
        self,
        coupon_id: int,
        product_id: int,
        code: Optional[str] = None,
        product_type: Optional[str] = None,
    ) -> Optional[CouponProductModel]:
        q = (CouponProductModel
             .select()
             .where(
                 (CouponProductModel.coupon == coupon_id) &
                 (CouponProductModel.product_id == product_id)
             ))
        if code:
            q = q.where(CouponProductModel.code == code)
        if product_type:
            q = q.where(CouponProductModel.product_type == product_type)
        return q.first()

    # ---------- Create ----------
    def add(self, data: CouponProductData) -> CouponProductData:
        # PK actual: (coupon, product_id). Si ya existe, actualiza (code, product_type, stock, status).
        rec = self._find_one(data.coupon_id, data.product_id)
        if rec:
            rec.code = data.code
            rec.product_type = data.product_type.value if hasattr(data.product_type, "value") else str(data.product_type)
            rec.stock = data.stock
            rec.status = data.status.value if hasattr(data.status, "value") else str(data.status)
            rec.save()
            return self._to_entity(rec)

        rec = CouponProductModel.create(
            coupon=data.coupon_id,
            product_id=data.product_id,
            code=data.code,
            product_type=data.product_type.value if hasattr(data.product_type, "value") else str(data.product_type),
            stock=data.stock,
            status=data.status.value if hasattr(data.status, "value") else str(data.status),
        )
        return self._to_entity(rec)

    def bulk_add(self, coupon_id: int, items: List[Dict]) -> List[CouponProductData]:
        out: List[CouponProductData] = []
        for it in items:
            entity = CouponProductData(
                coupon_id=coupon_id,
                product_id=int(it["product_id"]),
                code=str(it["code"]).strip(),
                product_type=str(it.get("product_type", "PRODUCT")).upper(),
                stock=(int(it["stock"]) if it.get("stock") is not None else None),
                status=str(it.get("status", "ACTIVE")).upper(),
            )
            out.append(self.add(entity))
        return out

    # ---------- Delete ----------
    def remove(self, coupon_id: int, product_id: int) -> bool:
        # Compat: borra por PK (coupon, product_id)
        q = (CouponProductModel
             .delete()
             .where(
                 (CouponProductModel.coupon == coupon_id) &
                 (CouponProductModel.product_id == product_id)
             ))
        return q.execute() > 0

    def remove_by_combo(
        self,
        coupon_id: int,
        product_id: int,
        code: Optional[str] = None,
        product_type: Optional[str] = None,
    ) -> int:
        q = (CouponProductModel
             .delete()
             .where(
                 (CouponProductModel.coupon == coupon_id) &
                 (CouponProductModel.product_id == product_id)
             ))
        if code:
            q = q.where(CouponProductModel.code == code)
        if product_type:
            q = q.where(CouponProductModel.product_type == product_type)
        return q.execute()

    def remove_all_for_coupon(self, coupon_id: int) -> int:
        q = CouponProductModel.delete().where(CouponProductModel.coupon == coupon_id)
        return q.execute()

    # ---------- Read ----------
    def list_products_by_coupon(self, coupon_id: int) -> List[Dict]:
        q = CouponProductModel.select().where(CouponProductModel.coupon == coupon_id)
        return [{
            "product_id": r.product_id,
            "code": r.code,
            "product_type": r.product_type,
            "stock": r.stock,
            "status": r.status,
        } for r in q]

    def list_coupons_by_product(self, product_id: int) -> List[int]:
        q = (CouponProductModel
             .select(CouponProductModel.coupon)
             .where(CouponProductModel.product_id == product_id)
             .group_by(CouponProductModel.coupon))
        return [r.coupon_id if hasattr(r, "coupon_id") else r.coupon.id for r in q]

    # ---------- Stock ----------
    def consume_one(
        self,
        coupon_id: int,
        product_id: int,
        code: Optional[str] = None,
        product_type: Optional[str] = None,
    ) -> Optional[Dict]:
        rec = self._find_one(coupon_id, product_id, code=code, product_type=product_type)
        if not rec:
            return None

        # Sin control de stock: no cambia nada
        if rec.stock is None:
            # Devuelve snapshot actual
            return {
                "coupon_id": coupon_id,
                "product_id": product_id,
                "code": rec.code,
                "product_type": rec.product_type,
                "stock": None,
                "status": rec.status,
            }

        # Con control de stock:
        if rec.stock <= 0:
            rec.status = "INACTIVE"
            rec.save()
            return {
                "coupon_id": coupon_id,
                "product_id": product_id,
                "code": rec.code,
                "product_type": rec.product_type,
                "stock": rec.stock,
                "status": rec.status,
            }

        rec.stock = rec.stock - 1
        if rec.stock <= 0:
            rec.status = "INACTIVE"
        rec.save()

        return {
            "coupon_id": coupon_id,
            "product_id": product_id,
            "code": rec.code,
            "product_type": rec.product_type,
            "stock": rec.stock,
            "status": rec.status,
        }
