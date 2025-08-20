from __future__ import annotations
from datetime import datetime
from typing import Optional, Any
from flask import Blueprint, request, jsonify, current_app

coupon_client_bp = Blueprint("coupon_client_api", __name__, url_prefix="/api/coupon-clients")

def _svc():
    cfg = current_app.config.get("coupon_client_services")
    if not cfg:
        raise RuntimeError("coupon_client_services not configured")
    return cfg["cmd"], cfg["qry"]

def _dt(v: Optional[str]) -> Optional[datetime]:
    if not v: return None
    return datetime.fromisoformat(str(v).replace("Z", "+00:00")).replace(tzinfo=None)

def _to_json(x) -> dict:
    return {
        "id": x.id,
        "coupon_id": x.coupon_id,
        "client_id": x.client_id,
        "code": x.code,
        "status": x.status.value,
        "valid_from": x.valid_from.isoformat() if x.valid_from else None,
        "valid_to": x.valid_to.isoformat() if x.valid_to else None,
        "used_at": x.used_at.isoformat() if x.used_at else None,
        "source_trigger_id": x.source_trigger_id,
        "source_order_id": x.source_order_id,
        "created_at": x.created_at.isoformat() if x.created_at else None,
    }

@coupon_client_bp.route("", methods=["POST"])
def assign_coupon_to_client():
    cmd, _ = _svc()
    data = request.get_json(silent=True) or {}
    try:
        created = cmd.assign_to_client(
            coupon_id   = int(data["coupon_id"]),
            client_id   = int(data["client_id"]),
            code        = str(data["code"]).strip(),
            valid_from  = _dt(data.get("valid_from")),
            valid_to    = _dt(data.get("valid_to")),
            source_trigger_id = (int(data["source_trigger_id"]) if data.get("source_trigger_id") is not None else None),
            source_order_id   = (int(data["source_order_id"]) if data.get("source_order_id") is not None else None),
        )
        return jsonify(_to_json(created)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@coupon_client_bp.route("/by-client/<int:client_id>", methods=["GET"])
def list_by_client(client_id: int):
    _cmd, qry = _svc()
    try:
        active_only = (request.args.get("active_only", "false").lower() in ("1","true","yes"))
        rows = qry.list_active_for_client(client_id) if active_only else qry.list_by_client(client_id)
        return jsonify([_to_json(r) for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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
