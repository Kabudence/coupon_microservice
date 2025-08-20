from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask import Blueprint, request, jsonify, current_app

from coupons.alianza.domain.entities.alianza import AlianzaEstado

alianza_bp = Blueprint("alianza_api", __name__, url_prefix="/api/alliances")


# coupons/alianza/interface/alianza_api.py
from flask import current_app

def _svc():
    pair = current_app.config.get("alianza_services")
    if pair:
        return pair

    services = current_app.config.get("coupon_services", {})
    cmd = services.get("alianza_command_service")
    qry = services.get("alianza_query_service")
    if not cmd or not qry:
        raise RuntimeError("alianza_services not configured in current_app.config")
    current_app.config["alianza_services"] = (cmd, qry)
    return cmd, qry


def _alianza_to_json(a) -> dict:
    return {
        "id": getattr(a, "id", None),
        "solicitante_negocio_id": getattr(a, "solicitante_negocio_id", None),
        "receptor_negocio_id": getattr(a, "receptor_negocio_id", None),
        "estado": getattr(getattr(a, "estado", None), "value", None) or getattr(a, "estado", None),
        "motivo": getattr(a, "motivo", None),
        "fecha_solicitud": getattr(a, "fecha_solicitud", None).isoformat() if getattr(a, "fecha_solicitud", None) else None,
        "fecha_respuesta": getattr(a, "fecha_respuesta", None).isoformat() if getattr(a, "fecha_respuesta", None) else None,
    }


# ---------- Crear solicitud ----------
@alianza_bp.route("", methods=["POST"])
def solicitar_alianza():
    """
    Body JSON:
    {
      "solicitante_negocio_id": 1,
      "receptor_negocio_id": 2,
      "motivo": "Opcional"
    }
    """
    cmd, _qry = _svc()
    data = request.get_json(silent=True) or {}
    try:
        s = int(data.get("solicitante_negocio_id"))
        r = int(data.get("receptor_negocio_id"))
        motivo = (data.get("motivo") or None)

        created = cmd.solicitar(s, r, motivo=motivo)
        return jsonify(_alianza_to_json(created)), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Lecturas ----------
@alianza_bp.route("", methods=["GET"])
def listar_alianzas():
    """
    Query params opcionales:
      ?negocio_id=123
      ?estado=PENDIENTE|ACEPTADA|RECHAZADA|CANCELADA|SUSPENDIDA
    """
    _cmd, qry = _svc()
    try:
        negocio_id = request.args.get("negocio_id", type=int)
        estado = request.args.get("estado", type=str)

        if negocio_id is not None:
            rows = qry.list_by_negocio(negocio_id)
        else:
            rows = qry.list_all()

        if estado:
            estado_enum = AlianzaEstado(estado)
            rows = [a for a in rows if a.estado == estado_enum]

        return jsonify([_alianza_to_json(a) for a in rows]), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alianza_bp.route("/<int:alianza_id>", methods=["GET"])
def obtener_alianza(alianza_id: int):
    _cmd, qry = _svc()
    try:
        row = qry.get_by_id(alianza_id)
        if not row:
            return jsonify({"error": "Alianza no encontrada"}), 404
        return jsonify(_alianza_to_json(row)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alianza_bp.route("/by-negocio/<int:negocio_id>", methods=["GET"])
def listar_por_negocio(negocio_id: int):
    _cmd, qry = _svc()
    try:
        rows = qry.list_by_negocio(negocio_id)
        return jsonify([_alianza_to_json(a) for a in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alianza_bp.route("/pendientes/recibidas", methods=["GET"])
def pendientes_recibidas():
    """
    ?negocio_id=ID (receptor)
    """
    _cmd, qry = _svc()
    try:
        negocio_id = request.args.get("negocio_id", type=int)
        if negocio_id is None:
            return jsonify({"error": "negocio_id es requerido"}), 400
        rows = qry.pendientes_recibidas(negocio_id)
        return jsonify([_alianza_to_json(a) for a in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alianza_bp.route("/pendientes/enviadas", methods=["GET"])
def pendientes_enviadas():
    """
    ?negocio_id=ID (solicitante)
    """
    _cmd, qry = _svc()
    try:
        negocio_id = request.args.get("negocio_id", type=int)
        if negocio_id is None:
            return jsonify({"error": "negocio_id es requerido"}), 400
        rows = qry.pendientes_enviadas(negocio_id)
        return jsonify([_alianza_to_json(a) for a in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alianza_bp.route("/activas", methods=["GET"])
def activas():
    """
    ?negocio_id=ID
    """
    _cmd, qry = _svc()
    try:
        negocio_id = request.args.get("negocio_id", type=int)
        if negocio_id is None:
            return jsonify({"error": "negocio_id es requerido"}), 400
        rows = qry.activas(negocio_id)
        return jsonify([_alianza_to_json(a) for a in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alianza_bp.route("/existe", methods=["GET"])
def existe_entre():
    """
    ?negocio_a=ID&negocio_b=ID
    """
    _cmd, qry = _svc()
    try:
        a = request.args.get("negocio_a", type=int)
        b = request.args.get("negocio_b", type=int)
        if a is None or b is None:
            return jsonify({"error": "negocio_a y negocio_b son requeridos"}), 400
        row = qry.exists_between(a, b)
        if not row:
            return jsonify({"exists": False}), 200
        return jsonify({"exists": True, **_alianza_to_json(row)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Acciones de estado ----------
def _actor_from_body():
    data = request.get_json(silent=True) or {}
    actor = data.get("actor_negocio_id")
    motivo = data.get("motivo")
    if actor is None:
        raise ValueError("actor_negocio_id es requerido")
    return int(actor), (motivo or None)

@alianza_bp.route("/<int:alianza_id>/aceptar", methods=["PUT"])
def aceptar(alianza_id: int):
    cmd, _qry = _svc()
    try:
        actor, _ = _actor_from_body()
        updated = cmd.aceptar(alianza_id, actor)
        return jsonify(_alianza_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@alianza_bp.route("/<int:alianza_id>/rechazar", methods=["PUT"])
def rechazar(alianza_id: int):
    cmd, _qry = _svc()
    try:
        actor, motivo = _actor_from_body()
        updated = cmd.rechazar(alianza_id, actor, motivo=motivo)
        return jsonify(_alianza_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@alianza_bp.route("/<int:alianza_id>/cancelar", methods=["PUT"])
def cancelar(alianza_id: int):
    cmd, _qry = _svc()
    try:
        actor, motivo = _actor_from_body()
        updated = cmd.cancelar(alianza_id, actor, motivo=motivo)
        return jsonify(_alianza_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@alianza_bp.route("/<int:alianza_id>/suspender", methods=["PUT"])
def suspender(alianza_id: int):
    cmd, _qry = _svc()
    try:
        actor, motivo = _actor_from_body()
        updated = cmd.suspender(alianza_id, actor, motivo=motivo)
        return jsonify(_alianza_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@alianza_bp.route("/<int:alianza_id>/reactivar", methods=["PUT"])
def reactivar(alianza_id: int):
    cmd, _qry = _svc()
    try:
        actor, motivo = _actor_from_body()
        updated = cmd.reactivar(alianza_id, actor, motivo=motivo)
        return jsonify(_alianza_to_json(updated)), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# --- ALIASES EN (para compatibilidad con el gateway/cliente) ---

@alianza_bp.get("/by-business/<int:negocio_id>")
def listar_por_negocio_en(negocio_id: int):
    return listar_por_negocio(negocio_id)

@alianza_bp.get("/pending/received")
def pendientes_recibidas_en():
    return pendientes_recibidas()

@alianza_bp.get("/pending/sent")
def pendientes_enviadas_en():
    return pendientes_enviadas()

@alianza_bp.get("/active")
def activas_en():
    return activas()

@alianza_bp.get("/exists")
def existe_entre_en():
    return existe_entre()

@alianza_bp.put("/<int:alianza_id>/accept")
def aceptar_en(alianza_id: int):
    return aceptar(alianza_id)

@alianza_bp.put("/<int:alianza_id>/reject")
def rechazar_en(alianza_id: int):
    return rechazar(alianza_id)

@alianza_bp.put("/<int:alianza_id>/cancel")
def cancelar_en(alianza_id: int):
    return cancelar(alianza_id)

@alianza_bp.put("/<int:alianza_id>/suspend")
def suspender_en(alianza_id: int):
    return suspender(alianza_id)

@alianza_bp.put("/<int:alianza_id>/reactivate")
def reactivar_en(alianza_id: int):
    return reactivar(alianza_id)
