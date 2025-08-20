from __future__ import annotations

from flask import Blueprint, request, jsonify, current_app

category_bp = Blueprint("coupon_category_api", __name__, url_prefix="/api/coupon-categories")


def _svc():
    # 1) intenta desde el dict principal
    services = current_app.config.get("coupon_services") or {}
    cmd = services.get("category_command_service")
    qry = services.get("category_query_service")

    # 2) fallback a tupla opcional
    if not cmd or not qry:
        tup = current_app.config.get("category_services")
        if tup and isinstance(tup, (list, tuple)) and len(tup) == 2:
            cmd, qry = tup

    if not cmd or not qry:
        raise RuntimeError("category services not configured in app.config")

    return cmd, qry


def _category_to_json(c) -> dict:
    return {
        "id": getattr(c, "id", None),
        "nombre": getattr(c, "nombre", None),
        "description": getattr(c, "description", None),
        "created_at": getattr(c, "created_at", None).isoformat() if getattr(c, "created_at", None) else None,
    }


@category_bp.route("", methods=["POST"])
def create_category():
    """
    Body:
    {
      "nombre": "SIMPLE",
      "description": "opcional"
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        nombre = (data.get("nombre") or "").strip()
        description = (data.get("description") or None)
        created = cmd.create(nombre=nombre, description=description)
        return jsonify(_category_to_json(created)), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route("", methods=["GET"])
def list_categories():
    """
    Query params opcionales:
      ?nombre=ExactMatch   (si se envía, devuelve 0..1 resultado)
    """
    _cmd, qry = _svc()
    try:
        nombre = request.args.get("nombre", type=str)
        if nombre:
            row = qry.get_by_nombre(nombre)
            return jsonify([] if row is None else [_category_to_json(row)]), 200
        rows = qry.list_all()
        return jsonify([_category_to_json(r) for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id: int):
    _cmd, qry = _svc()
    try:
        row = qry.get_by_id(category_id)
        if not row:
            return jsonify({"error": "Category not found"}), 404
        return jsonify(_category_to_json(row)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id: int):
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        nombre = (data.get("nombre") or "").strip()
        description = (data.get("description") or None)
        updated = cmd.update(id_=category_id, nombre=nombre, description=description)
        return jsonify(_category_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@category_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int):
    cmd, _qry = _svc()
    try:
        ok = cmd.delete(category_id)
        if not ok:
            return jsonify({"error": "Category not found"}), 404
        return jsonify({"deleted": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
