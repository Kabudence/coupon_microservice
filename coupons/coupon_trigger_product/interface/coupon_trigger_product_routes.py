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
            product_type=product_type,
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
            product_type=product_type,
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


# =============== NUEVO: Resolver triggers por ítems comprados ===============
@coupon_trigger_product_bp.route("/by-items", methods=["POST", "OPTIONS"])
def resolve_triggers_by_items():
    """
    Dado un listado de ítems comprados (PRODUCT / SERVICE), devuelve
    los mappings que aplican, respetando min_quantity / min_amount.
    Body:
    {
      "business_id": 22,            # opcional
      "items": [
        {"product_type":"PRODUCT","product_id":123,"quantity":2,"amount":"49.90"},
        ...
      ]
    }
    """
    if request.method == "OPTIONS":
        # Respuesta vacía para preflight CORS
        return ("", 200, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        })

    _cmd, qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        raw_items = data.get("items")
        if not isinstance(raw_items, list) or not raw_items:
            raise ValueError("items must be a non-empty list")

        resolved = []
        seen = set()  # evitar duplicados (product_id, coupon_id, product_type)

        for it in raw_items:
            if not isinstance(it, dict):
                continue

            ptype = _parse_product_type(it)
            pid = it.get("product_id", it.get("id"))
            product_id = _require_positive_int(pid, "product_id")

            qty = int(it.get("quantity", 1))
            if qty < 1:
                qty = 1
            amount = _optional_decimal(it.get("amount"), "amount")

            # asumimos product_trigger_id == product_id
            mappings = qry.list_coupons_by_trigger(product_id)

            for m in mappings:
                md = m if isinstance(m, dict) else m.to_dict()
                m_ptype = (md.get("product_type") or "PRODUCT").upper()
                if m_ptype not in ("PRODUCT", "SERVICE"):
                    m_ptype = "PRODUCT"

                if m_ptype != ptype:
                    continue

                min_q = int(md.get("min_quantity") or 1)
                min_a = md.get("min_amount")
                min_a = Decimal(str(min_a)) if min_a is not None else None

                if qty < min_q:
                    continue
                if min_a is not None and (amount is None or amount < min_a):
                    continue

                coupon_id = _require_positive_int(md.get("coupon_id"), "coupon_id")
                key = (product_id, coupon_id, ptype)
                if key in seen:
                    continue
                seen.add(key)

                resolved.append({
                    "product_type": ptype,
                    "product_id": product_id,
                    "coupon_id": coupon_id,
                    "min_quantity": min_q,
                    "min_amount": str(min_a) if min_a is not None else None
                })

        return jsonify(resolved), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
