from __future__ import annotations

from typing import Any, List, Optional
from flask import Blueprint, request, jsonify, current_app

coupon_product_bp = Blueprint("coupon_product_api", __name__, url_prefix="/api/coupon-products")


def _svc():
    """
    Helper: obtiene services desde current_app.config["coupon_services"].
    Espera llaves:
      - "coupon_product_command_service"
      - "coupon_product_query_service"
    """
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


@coupon_product_bp.route("", methods=["POST"])
def add_mapping():
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

        created = cmd.add_mapping(coupon_id=coupon_id, product_id=product_id)
        return jsonify({"coupon_id": created.coupon_id, "product_id": created.product_id}), 201
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
      "product_ids": [555, 556, 557]
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        coupon_id = _require_positive_int(data.get("coupon_id"), "coupon_id")
        product_ids_raw = data.get("product_ids")
        if not isinstance(product_ids_raw, list):
            raise ValueError("product_ids must be a list of integers")
        product_ids: List[int] = [_require_positive_int(pid, "product_id") for pid in product_ids_raw]

        created_list = cmd.bulk_add_mappings(coupon_id=coupon_id, product_ids=product_ids)
        return jsonify([{"coupon_id": m.coupon_id, "product_id": m.product_id} for m in created_list]), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("/by-coupon/<int:coupon_id>", methods=["GET"])
def list_products_by_coupon(coupon_id: int):
    _cmd, qry = _svc()
    try:
        result = qry.list_products_by_coupon(coupon_id)
        return jsonify(result), 200  # lista de product_id (int)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("/by-product/<int:product_id>", methods=["GET"])
def list_coupons_by_product(product_id: int):
    _cmd, qry = _svc()
    try:
        result = qry.list_coupons_by_product(product_id)
        return jsonify(result), 200  # lista de coupon_id (int)
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
            # si no existía el mapping:
            return jsonify({"deleted": False, "message": "Mapping not found"}), 404
        return jsonify({"deleted": True}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_product_bp.route("/by-coupon/<int:coupon_id>", methods=["DELETE"])
def remove_all_for_coupon(coupon_id: int):
    cmd, _qry = _svc()
    try:
        deleted_count = cmd.remove_all_for_coupon(coupon_id)
        return jsonify({"deleted_count": deleted_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
