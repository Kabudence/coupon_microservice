# coupons/product_coupon/interface/coupon_product_http.py
from __future__ import annotations
from typing import Any, List, Optional, Dict
from flask import Blueprint, request, jsonify, current_app

coupon_product_bp = Blueprint("coupon_product_api", __name__, url_prefix="/api/coupon-products")


def _svc():
    services = current_app.config.get("coupon_services")
    if not services:
        raise RuntimeError("coupon_services not configured in current_app.config")
    return services["coupon_product_command_service"], services["coupon_product_query_service"]


def _require_positive_int(value: Any, field: str) -> int:
    if value is None:
        raise ValueError(f"{field} is required")
    try:
        iv = int(value)
    except Exception:
        raise ValueError(f"{field} must be an integer")
    if iv <= 0:
        raise ValueError(f"{field} must be > 0")
    return iv


def _parse_optional_nonneg_int(value: Any, field: str) -> Optional[int]:
    if value is None:
        return None
    try:
        iv = int(value)
    except Exception:
        raise ValueError(f"{field} must be an integer")
    if iv < 0:
        raise ValueError(f"{field} must be >= 0")
    return iv


@coupon_product_bp.route("", methods=["POST"])
def add_mapping():
    """
    Body (JSON):
    {
      "coupon_id": 123,
      "product_id": 555,
      "code": "SKU-555",
      "product_type": "PRODUCT" | "SERVICE",
      "stock": 10,                   # opcional (>=0)
      "status": "ACTIVE"|"INACTIVE"  # opcional (default ACTIVE)
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")
        product_id = _require_positive_int(data.get("product_id"), "product_id")
        code = (data.get("code") or "").strip()
        if not code:
            raise ValueError("code is required")
        ptype = (data.get("product_type") or "").strip().upper()
        if ptype not in ("PRODUCT", "SERVICE"):
            raise ValueError("product_type must be PRODUCT or SERVICE")

        stock = _parse_optional_nonneg_int(data.get("stock"), "stock")
        status = (data.get("status") or "ACTIVE").strip().upper()
        if status not in ("ACTIVE", "INACTIVE"):
            raise ValueError("status must be ACTIVE or INACTIVE")

        created = cmd.add_mapping(
            coupon_id=coupon_id,
            product_id=product_id,
            code=code,
            product_type=ptype,
            stock=stock,
            status=status,
        )
        return jsonify(created.to_dict()), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("/bulk", methods=["POST"])
def bulk_add_mappings():
    """
    Body (JSON):
    {
      "coupon_id": 123,
      "items": [
        {"product_id": 555, "code": "SKU-555", "product_type": "PRODUCT", "stock": 10, "status": "ACTIVE"},
        {"product_id": 777, "code": "SRV-777", "product_type": "SERVICE", "status": "INACTIVE"}
      ]
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")
        items = data.get("items")
        if not isinstance(items, list):
            raise ValueError("items must be a list")

        norm_items: List[Dict] = []
        for it in items:
            pid = _require_positive_int(it.get("product_id"), "product_id")
            code = (it.get("code") or "").strip()
            if not code:
                raise ValueError("each item.code is required")
            ptype = (it.get("product_type") or "").strip().upper()
            if ptype not in ("PRODUCT", "SERVICE"):
                raise ValueError("each item.product_type must be PRODUCT or SERVICE")

            stock = _parse_optional_nonneg_int(it.get("stock"), "stock")
            status = (it.get("status", "ACTIVE") or "ACTIVE").strip().upper()
            if status not in ("ACTIVE", "INACTIVE"):
                raise ValueError("each item.status must be ACTIVE or INACTIVE")

            norm_items.append({
                "product_id": pid,
                "code": code,
                "product_type": ptype,
                "stock": stock,
                "status": status,
            })

        created_list = cmd.bulk_add_mappings(coupon_id=coupon_id, items=norm_items)
        return jsonify([m.to_dict() for m in created_list]), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("/by-coupon/<int:coupon_id>", methods=["GET"])
def list_products_by_coupon(coupon_id: int):
    _cmd, qry = _svc()
    try:
        result = qry.list_products_by_coupon(coupon_id)
        return jsonify(result), 200  # [{product_id, code, product_type, stock, status}]
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("/by-product/<int:product_id>", methods=["GET"])
def list_coupons_by_product(product_id: int):
    _cmd, qry = _svc()
    try:
        result = qry.list_coupons_by_product(product_id)
        return jsonify(result), 200  # [coupon_id]
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("", methods=["DELETE"])
def remove_mapping():
    """
    Body (JSON):
    {
      "coupon_id": 123,
      "product_id": 555
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")
        product_id = _require_positive_int(data.get("product_id"), "product_id")

        ok = cmd.remove_mapping(coupon_id=coupon_id, product_id=product_id)
        if not ok:
            return jsonify({"deleted": False, "message": "Mapping not found"}), 404
        return jsonify({"deleted": True}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("/remove-by", methods=["DELETE"])
def remove_by_combo():
    """
    Body (JSON):
    {
      "coupon_id": 123,
      "product_id": 555,
      "code": "SKU-555",             # opcional (si se envía, filtra)
      "product_type": "PRODUCT"      # opcional (si se envía, filtra)
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")
        product_id = _require_positive_int(data.get("product_id"), "product_id")
        code = (data.get("code") or "").strip() or None
        product_type = (data.get("product_type") or "").strip().upper() or None

        deleted = cmd.remove_by_combo(coupon_id, product_id, code=code, product_type=product_type)
        return jsonify({"deleted_count": deleted}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== NUEVO: consumir 1 de stock =====
@coupon_product_bp.route("/consume", methods=["PUT"])
def consume_one():
    """
    Body (JSON):
    {
      "coupon_id": 123,
      "product_id": 555,
      "code": "SKU-555",          # opcional (si envías, valida por code también)
      "product_type": "PRODUCT"   # opcional (si envías, valida por tipo también)
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")
        product_id = _require_positive_int(data.get("product_id"), "product_id")
        code = (data.get("code") or "").strip() or None
        product_type = (data.get("product_type") or "").strip().upper() or None
        if product_type and product_type not in ("PRODUCT", "SERVICE"):
            raise ValueError("product_type must be PRODUCT or SERVICE")

        res = cmd.consume_one(coupon_id, product_id, code=code, product_type=product_type)
        if not res:
            return jsonify({"error": "mapping not found"}), 404
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
