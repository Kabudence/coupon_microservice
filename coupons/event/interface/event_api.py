from __future__ import annotations

from flask import Blueprint, request, jsonify, current_app

event_bp = Blueprint("coupon_event_api", __name__, url_prefix="/api/coupon-events")


def _svc():
    services = current_app.config.get("coupon_services")
    if not services:
        raise RuntimeError("coupon_services not configured in current_app.config")
    return services["event_command_service"], services["event_query_service"]


def _event_to_json(e) -> dict:
    return {
        "id": getattr(e, "id", None),
        "nombre": getattr(e, "nombre", None),
        "description": getattr(e, "description", None),
        "created_at": getattr(e, "created_at", None).isoformat() if getattr(e, "created_at", None) else None,
    }


@event_bp.route("", methods=["POST"])
def create_event():
    """
    Body:
    {
      "nombre": "Black Friday",
      "description": "opcional"
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        nombre = (data.get("nombre") or "").strip()
        description = (data.get("description") or None)
        created = cmd.create(nombre=nombre, description=description)
        return jsonify(_event_to_json(created)), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@event_bp.route("", methods=["GET"])
def list_events():
    """
    Query params opcionales:
      ?nombre=ExactMatch   (si se envía, devuelve 0..1 resultado)
    """
    _cmd, qry = _svc()
    try:
        nombre = request.args.get("nombre", type=str)
        if nombre:
            row = qry.get_by_nombre(nombre)
            return jsonify([] if row is None else [_event_to_json(row)]), 200
        rows = qry.list_all()
        return jsonify([_event_to_json(r) for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@event_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id: int):
    _cmd, qry = _svc()
    try:
        row = qry.get_by_id(event_id)
        if not row:
            return jsonify({"error": "Event not found"}), 404
        return jsonify(_event_to_json(row)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@event_bp.route("/<int:event_id>", methods=["PUT"])
def update_event(event_id: int):
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        nombre = (data.get("nombre") or "").strip()
        description = (data.get("description") or None)
        updated = cmd.update(id_=event_id, nombre=nombre, description=description)
        return jsonify(_event_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@event_bp.route("/<int:event_id>", methods=["DELETE"])
def delete_event(event_id: int):
    cmd, _qry = _svc()
    try:
        ok = cmd.delete(event_id)
        if not ok:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"deleted": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
