from __future__ import annotations

from decimal import Decimal
from typing import Any, List, Optional

from flask import Blueprint, request, jsonify, current_app

coupon_trigger_product_bp = Blueprint(
    "coupon_trigger_product_api",
    __name__,
    url_prefix="/api/coupon-trigger-products"
)


def _svc():
    services = current_app.config.get("coupon_services")
    if not services:
        raise RuntimeError("coupon_services not configured in current_app.config")
    return (
        services["coupon_trigger_product_command_service"],
        services["coupon_trigger_product_query_service"],
    )


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


def _optional_decimal(value: Any, field: str) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        raise ValueError(f"{field} must be a valid number")


def _parse_product_type(data: dict) -> str:
    # acepta 'product_type' o alias 'type'
    ptype = (data.get("product_type") or data.get("type") or "PRODUCT").strip().upper()
    if ptype not in ("PRODUCT", "SERVICE"):
        raise ValueError("product_type must be PRODUCT or SERVICE")
    return ptype


@coupon_trigger_product_bp.route("", methods=["POST"])
def add_mapping():
    """
    Body JSON:
    {
      "product_trigger_id": 777,
      "coupon_id": 123,
      "product_type": "PRODUCT" | "SERVICE",  # <-- NUEVO (obligatorio)
      "min_quantity": 1,                      # opcional
      "min_amount":  null                     # opcional
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        product_trigger_id = _require_positive_int(data.get("product_trigger_id"), "product_trigger_id")
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")
        product_type = _parse_product_type(data)
        min_quantity = int(data.get("min_quantity", 1))
        if min_quantity < 1:
            raise ValueError("min_quantity must be >= 1")
        min_amount = _optional_decimal(data.get("min_amount"), "min_amount")

        created = cmd.add_mapping(
            product_trigger_id=product_trigger_id,
            coupon_id=coupon_id,
            product_type=product_type,         # <-- NUEVO
            min_quantity=min_quantity,
            min_amount=min_amount,
        )
        return jsonify(created.to_dict()), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_trigger_product_bp.route("/bulk", methods=["POST"])
def bulk_add_mappings():
    """
    Body JSON:
    {
      "coupon_id": 123,
      "product_trigger_ids": [777, 778, 779],
      "product_type": "PRODUCT" | "SERVICE",  # <-- NUEVO (para todos)
      "min_quantity": 1,                      # opcional
      "min_amount": null                      # opcional
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")

        raw_ids = data.get("product_trigger_ids")
        if not isinstance(raw_ids, list) or not raw_ids:
            raise ValueError("product_trigger_ids must be a non-empty list of integers")
        product_trigger_ids: List[int] = [_require_positive_int(v, "product_trigger_id") for v in raw_ids]

        product_type = _parse_product_type(data)
        min_quantity = int(data.get("min_quantity", 1))
        if min_quantity < 1:
            raise ValueError("min_quantity must be >= 1")
        min_amount = _optional_decimal(data.get("min_amount"), "min_amount")

        created_list = cmd.bulk_add_mappings(
            coupon_id=coupon_id,
            product_trigger_ids=product_trigger_ids,
            product_type=product_type,         # <-- NUEVO
            min_quantity=min_quantity,
            min_amount=min_amount,
        )
        return jsonify([m.to_dict() for m in created_list]), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_trigger_product_bp.route("/by-coupon/<int:coupon_id>", methods=["GET"])
def list_triggers_by_coupon(coupon_id: int):
    _cmd, qry = _svc()
    try:
        rows = qry.list_triggers_by_coupon(coupon_id)
        return jsonify([m.to_dict() for m in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_trigger_product_bp.route("/by-trigger/<int:product_trigger_id>", methods=["GET"])
def list_coupons_by_trigger(product_trigger_id: int):
    _cmd, qry = _svc()
    try:
        result = qry.list_coupons_by_trigger(product_trigger_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_trigger_product_bp.route("", methods=["DELETE"])
def remove_mapping():
    """
    Body JSON:
    { "product_trigger_id": 777, "coupon_id": 123 }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        product_trigger_id = _require_positive_int(data.get("product_trigger_id"), "product_trigger_id")
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")

        ok = cmd.remove_mapping(product_trigger_id=product_trigger_id, coupon_id=coupon_id)
        if not ok:
            return jsonify({"deleted": False, "message": "Mapping not found"}), 404
        return jsonify({"deleted": True}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_trigger_product_bp.route("/by-coupon/<int:coupon_id>", methods=["DELETE"])
def remove_all_for_coupon(coupon_id: int):
    cmd, _qry = _svc()
    try:
        deleted_count = cmd.remove_all_for_coupon(coupon_id)
        return jsonify({"deleted_count": deleted_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
