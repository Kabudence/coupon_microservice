# coupons/coupons_client/interface/coupon_client_routes.py
from __future__ import annotations
from datetime import datetime
from typing import Optional
from flask import Blueprint, request, jsonify, current_app

coupon_client_bp = Blueprint("coupon_client_api", __name__, url_prefix="/api/coupon-clients")

# -----------------------------------------------------------
# Resolver servicios desde la config:
# - O bien: app.config["coupon_client_services"] = {"cmd":..., "qry":...}
# - O bien: app.config["coupon_services"]["coupon_client_command_service"] / ["coupon_client_query_service"]
# -----------------------------------------------------------
def _svc():
    cfg = current_app.config.get("coupon_client_services")
    if cfg and "cmd" in cfg and "qry" in cfg:
        return cfg["cmd"], cfg["qry"]

    all_services = current_app.config.get("coupon_services")
    if not all_services:
        raise RuntimeError("coupon_services not configured")

    cmd = all_services.get("coupon_client_command_service")
    qry = all_services.get("coupon_client_query_service")
    if not cmd or not qry:
        raise RuntimeError(
            "coupon_client services not found in coupon_services "
            "(expected keys: 'coupon_client_command_service' and 'coupon_client_query_service')"
        )
    return cmd, qry

def _dt(v: Optional[str]) -> Optional[datetime]:
    if not v:
        return None
    # admite ...Z
    return datetime.fromisoformat(str(v).replace("Z", "+00:00")).replace(tzinfo=None)

def _to_json(x) -> dict:
    # status puede ser Enum o string
    status = getattr(x, "status", None)
    if hasattr(status, "value"):
        status = status.value
    elif status is not None:
        status = str(status)

    def _iso(attr: str):
        val = getattr(x, attr, None)
        return val.isoformat() if val else None

    return {
        "id": getattr(x, "id", None),
        "coupon_id": getattr(x, "coupon_id", None),
        "client_id": getattr(x, "client_id", None),
        "code": getattr(x, "code", ""),
        "status": status,
        "valid_from": _iso("valid_from"),
        "valid_to": _iso("valid_to"),
        "used_at": _iso("used_at"),
        "source_trigger_id": getattr(x, "source_trigger_id", None),
        "source_order_id": getattr(x, "source_order_id", None),
        "created_at": _iso("created_at"),
    }

# ----------------- CREATE -----------------
@coupon_client_bp.route("", methods=["POST"])
def assign_coupon_to_client():
    cmd, _ = _svc()
    data = request.get_json(silent=True) or {}
    try:
        # Requeridos
        coupon_id = int(data["coupon_id"])
        client_id = int(data["client_id"])

        # Opcionales
        code = str(data.get("code", "") or "").strip()

        # Aliases compatibles con gateway:
        # - origin_ref -> source_order_id
        # - expires_at -> valid_to
        source_trigger_id = data.get("source_trigger_id")
        if source_trigger_id is not None:
            source_trigger_id = int(source_trigger_id)

        source_order_id = data.get("source_order_id", data.get("origin_ref"))
        if source_order_id is not None:
            source_order_id = int(source_order_id)

        valid_from = _dt(data.get("valid_from"))
        valid_to   = _dt(data.get("valid_to") or data.get("expires_at"))

        created = cmd.assign_to_client(
            coupon_id=coupon_id,
            client_id=client_id,
            code=code,
            valid_from=valid_from,
            valid_to=valid_to,
            source_trigger_id=source_trigger_id,
            source_order_id=source_order_id,
        )
        return jsonify(_to_json(created)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------------- LIST con filtros (root) -----------------
@coupon_client_bp.route("", methods=["GET"])
def list_with_filters():
    _cmd, qry = _svc()
    try:
        client_id = request.args.get("client_id", type=int)
        active_only = (request.args.get("active_only", "false").lower() in ("1", "true", "yes"))

        if client_id is None:
            return jsonify({"error": "client_id is required"}), 400

        rows = qry.list_active_for_client(client_id) if active_only else qry.list_by_client(client_id)
        return jsonify([_to_json(r) for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------------- LIST por cliente (legacy) -----------------
@coupon_client_bp.route("/by-client/<int:client_id>", methods=["GET"])
def list_by_client(client_id: int):
    _cmd, qry = _svc()
    try:
        active_only = (request.args.get("active_only", "false").lower() in ("1", "true", "yes"))
        rows = qry.list_active_for_client(client_id) if active_only else qry.list_by_client(client_id)
        return jsonify([_to_json(r) for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------------- GET por id -----------------
@coupon_client_bp.route("/<int:cc_id>", methods=["GET"])
def get_cc(cc_id: int):
    _cmd, qry = _svc()
    try:
        row = qry.get_by_id(cc_id)
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(_to_json(row)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------------- REDEEM (alias nuevo) -----------------
@coupon_client_bp.route("/<int:cc_id>/redeem", methods=["PUT"])
def redeem_cc(cc_id: int):
    cmd, _ = _svc()
    data = request.get_json(silent=True) or {}
    try:
        updated = cmd.mark_used(cc_id, data.get("order_id"))
        if not updated:
            return jsonify({"error": "not found"}), 404
        return jsonify(_to_json(updated)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------- LEGACY: /use -------------
@coupon_client_bp.route("/<int:cc_id>/use", methods=["PUT"])
def mark_used(cc_id: int):
    cmd, _ = _svc()
    data = request.get_json(silent=True) or {}
    try:
        updated = cmd.mark_used(cc_id, data.get("order_id"))
        if not updated:
            return jsonify({"error": "not found"}), 404
        return jsonify(_to_json(updated)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ----------- EXPIRE (placeholder) -------------
@coupon_client_bp.route("/<int:cc_id>/expire", methods=["PUT"])
def expire_cc(cc_id: int):
    return jsonify({"error": "expire not implemented"}), 501

# ----------------- DELETE -----------------
@coupon_client_bp.route("/<int:cc_id>", methods=["DELETE"])
def delete_cc(cc_id: int):
    cmd, _ = _svc()
    try:
        ok = cmd.delete(cc_id)
        if not ok:
            return jsonify({"error": "not found"}), 404
        return jsonify({"deleted": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

