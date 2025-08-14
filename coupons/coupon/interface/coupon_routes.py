from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from flask import Blueprint, request, jsonify, current_app

coupon_bp = Blueprint("coupon_api", __name__, url_prefix="/api/coupons")


def _svc():
    """
    Helper: obtiene services desde current_app.config["coupon_services"].
    Espera llaves:
      - "coupon_command_service"
      - "coupon_query_service"
    """
    services = current_app.config.get("coupon_services")
    if not services:
        raise RuntimeError("coupon_services not configured in current_app.config")
    return services["coupon_command_service"], services["coupon_query_service"]


def _parse_datetime(value: Optional[str], field: str) -> Optional[datetime]:
    if value is None:
        return None
    try:
        # ISO 8601 (e.g., "2025-08-14T12:34:56") o "2025-08-14 12:34:56"
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        raise ValueError(f"{field} must be ISO8601 datetime (e.g. 2025-08-14T12:34:56)")


def _parse_decimal(value: Optional[Any], field: str) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        raise ValueError(f"{field} must be a number")


def _coupon_to_json(c) -> dict:
    # Si tu entidad tiene .to_dict(), podrías retornar c.to_dict() directo.
    # Aquí lo normalizo explícitamente para evitar sorpresas.
    return {
        "id": getattr(c, "id", None),
        "business_id": getattr(c, "business_id", None),
        "coupon_type_id": getattr(c, "coupon_type_id", None),
        "name": getattr(c, "name", None),
        "description": getattr(c, "description", None),
        "discount_type_id": getattr(c, "discount_type_id", None),
        "value": str(getattr(c, "value", None)) if getattr(c, "value", None) is not None else None,
        "max_discount": str(getattr(c, "max_discount", None)) if getattr(c, "max_discount", None) is not None else None,
        "start_date": getattr(c, "start_date", None).isoformat() if getattr(c, "start_date", None) else None,
        "end_date": getattr(c, "end_date", None).isoformat() if getattr(c, "end_date", None) else None,
        "max_uses": getattr(c, "max_uses", None),
        "code": getattr(c, "code", None),
        "event_name": getattr(c, "event_name", None),
        "is_shared_alliances": getattr(c, "is_shared_alliances", False),
        "status": getattr(getattr(c, "status", None), "value", None) or getattr(c, "status", None),
        "created_at": getattr(c, "created_at", None).isoformat() if getattr(c, "created_at", None) else None,
    }


@coupon_bp.route("", methods=["POST"])
def create_coupon():
    """
    Body JSON esperado:
    {
      "business_id": 123,
      "name": "WELCOME10",
      "discount_type_id": 1,             // PORCENTAJE/MONTO
      "value": 10.0,                     // según discount_type
      "start_date": "2025-08-14T00:00:00",
      "end_date": "2025-09-14T00:00:00",
      "coupon_type_id": 1,               // opcional
      "description": "10% up to 50",
      "max_discount": 50.0,              // opcional
      "max_uses": 1000,                  // opcional
      "code": "WELCOME10",               // opcional
      "event_name": null,                // opcional
      "is_shared_alliances": false,      // opcional
      "status": "ACTIVE"                 // opcional
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}

    try:
        business_id = int(data.get("business_id"))
        name = (data.get("name") or "").strip()
        discount_type_id = int(data.get("discount_type_id"))
        value = _parse_decimal(data.get("value"), "value")

        start_date = _parse_datetime(data.get("start_date"), "start_date")
        end_date = _parse_datetime(data.get("end_date"), "end_date")

        coupon_type_id = int(data["coupon_type_id"]) if data.get("coupon_type_id") is not None else None
        description = (data.get("description") or None)
        max_discount = _parse_decimal(data.get("max_discount"), "max_discount")
        max_uses = int(data["max_uses"]) if data.get("max_uses") is not None else None
        code = (data.get("code") or None)
        event_name = (data.get("event_name") or None)
        is_shared_alliances = bool(data.get("is_shared_alliances", False))
        status = (data.get("status") or "ACTIVE")

        created = cmd.create(
            business_id=business_id,
            name=name,
            discount_type_id=discount_type_id,
            value=value,
            start_date=start_date,
            end_date=end_date,
            coupon_type_id=coupon_type_id,
            description=description,
            max_discount=max_discount,
            max_uses=max_uses,
            code=code,
            event_name=event_name,
            is_shared_alliances=is_shared_alliances,
            status=status,  # CouponStatus o string aceptado por la Entity
        )
        return jsonify(_coupon_to_json(created)), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_bp.route("", methods=["GET"])
def list_coupons():
    """
    Query params opcionales:
      ?business_id=123
      ?code=WELCOME10
      ?active_only=true
    """
    _cmd, qry = _svc()
    try:
        business_id = request.args.get("business_id", type=int)
        code = request.args.get("code", type=str)
        active_only = request.args.get("active_only", default="false").lower() in ("1", "true", "yes")

        if code:
            row = qry.find_by_code(code)
            if not row:
                return jsonify([]), 200
            return jsonify([_coupon_to_json(row)]), 200

        if business_id is not None:
            rows = qry.find_by_business(business_id)
            if active_only:
                now = datetime.utcnow()
                rows = [c for c in rows if c.start_date <= now <= c.end_date]
            return jsonify([_coupon_to_json(r) for r in rows]), 200

        # default: list_all (posible filtro active_only)
        rows = qry.list_all()
        if active_only:
            now = datetime.utcnow()
            rows = [c for c in rows if c.start_date <= now <= c.end_date]
        return jsonify([_coupon_to_json(r) for r in rows]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_bp.route("/<int:coupon_id>", methods=["GET"])
def get_coupon(coupon_id: int):
    _cmd, qry = _svc()
    try:
        row = qry.get_by_id(coupon_id)
        if not row:
            return jsonify({"error": "Coupon not found"}), 404
        return jsonify(_coupon_to_json(row)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_bp.route("/<int:coupon_id>", methods=["PUT"])
def update_coupon(coupon_id: int):
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        business_id = int(data.get("business_id"))
        name = (data.get("name") or "").strip()
        discount_type_id = int(data.get("discount_type_id"))
        value = _parse_decimal(data.get("value"), "value")

        start_date = _parse_datetime(data.get("start_date"), "start_date")
        end_date = _parse_datetime(data.get("end_date"), "end_date")

        coupon_type_id = int(data["coupon_type_id"]) if data.get("coupon_type_id") is not None else None
        description = (data.get("description") or None)
        max_discount = _parse_decimal(data.get("max_discount"), "max_discount")
        max_uses = int(data["max_uses"]) if data.get("max_uses") is not None else None
        code = (data.get("code") or None)
        event_name = (data.get("event_name") or None)
        is_shared_alliances = bool(data.get("is_shared_alliances", False))
        status = (data.get("status") or "ACTIVE")

        updated = cmd.update(
            id_=coupon_id,
            business_id=business_id,
            name=name,
            discount_type_id=discount_type_id,
            value=value,
            start_date=start_date,
            end_date=end_date,
            coupon_type_id=coupon_type_id,
            description=description,
            max_discount=max_discount,
            max_uses=max_uses,
            code=code,
            event_name=event_name,
            is_shared_alliances=is_shared_alliances,
            status=status,
        )
        return jsonify(_coupon_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_bp.route("/<int:coupon_id>", methods=["DELETE"])
def delete_coupon(coupon_id: int):
    cmd, _qry = _svc()
    try:
        ok = cmd.delete(coupon_id)
        if not ok:
            return jsonify({"error": "Coupon not found"}), 404
        return jsonify({"deleted": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_bp.route("/by-code/<code>", methods=["GET"])
def find_by_code(code: str):
    _cmd, qry = _svc()
    try:
        row = qry.find_by_code(code)
        if not row:
            return jsonify({"error": "Coupon not found"}), 404
        return jsonify(_coupon_to_json(row)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_bp.route("/by-business/<int:business_id>", methods=["GET"])
def list_by_business(business_id: int):
    _cmd, qry = _svc()
    try:
        rows = qry.find_by_business(business_id)
        return jsonify([_coupon_to_json(r) for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_bp.route("/active/now", methods=["GET"])
def list_active_now():
    _cmd, qry = _svc()
    try:
        now = datetime.utcnow()
        rows = qry.list_active_in_window(now)
        return jsonify([_coupon_to_json(r) for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
