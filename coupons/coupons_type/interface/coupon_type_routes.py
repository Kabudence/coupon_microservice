# coupons/coupons_type/api/coupon_type_routes.py
from flask import Blueprint, request, jsonify, current_app

coupon_type_bp = Blueprint("coupon_type_api", __name__, url_prefix="/api/coupon-types")


def _svc():
    """
    Helper: obtiene los services desde app.config["coupon_services"].
    """
    services = current_app.config.get("coupon_services")
    if not services:
        raise RuntimeError("coupon_services not configured in current_app.config")
    return (
        services["coupon_type_command_service"],
        services["coupon_type_query_service"],
    )


@coupon_type_bp.route("", methods=["POST"])
def create_coupon_type():
    """
    Body (JSON):
    {
      "name": "SIMPLE",
      "description": "Simple coupons"
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    description = data.get("description")

    try:
        created = cmd.create(name=name, description=description)
        return jsonify({
            "id": created.id,
            "name": created.name,
            "description": created.description
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_type_bp.route("", methods=["GET"])
def list_coupon_types():
    _cmd, qry = _svc()
    try:
        rows = qry.list_all()
        return jsonify([
            {"id": r.id, "name": r.name, "description": r.description}
            for r in rows
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_type_bp.route("/<int:coupon_type_id>", methods=["GET"])
def get_coupon_type(coupon_type_id: int):
    _cmd, qry = _svc()
    try:
        row = qry.get_by_id(coupon_type_id)
        if not row:
            return jsonify({"error": "CouponType not found"}), 404
        return jsonify({"id": row.id, "name": row.name, "description": row.description}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_type_bp.route("/<int:coupon_type_id>", methods=["PUT"])
def update_coupon_type(coupon_type_id: int):
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    description = data.get("description")

    try:
        updated = cmd.update(coupon_type_id, name=name, description=description)
        return jsonify({
            "id": updated.id,
            "name": updated.name,
            "description": updated.description
        }), 200
    except ValueError as ve:
        # ej: "CouponType not found." o validaciones
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@coupon_type_bp.route("/<int:coupon_type_id>", methods=["DELETE"])
def delete_coupon_type(coupon_type_id: int):
    cmd, _qry = _svc()
    try:
        ok = cmd.delete(coupon_type_id)
        if not ok:
            # Si el repo devuelve False cuando no existe:
            return jsonify({"error": "CouponType not found"}), 404
        return jsonify({"deleted": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
