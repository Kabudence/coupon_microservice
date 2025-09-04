from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional, Tuple

from flask import Blueprint, request, jsonify, current_app

from payment.checkout.application.command.checkout_session_command_service import (
    CheckoutSessionCommandService,
)
from payment.checkout.application.queries.checkout_session_query_service import (
    CheckoutSessionQueryService,
)


# --------------------------
# Helpers (parseo/validación)
# --------------------------
def _get_services() -> Tuple[CheckoutSessionCommandService, CheckoutSessionQueryService]:
    services = current_app.config.get("services") or {}
    cmd: CheckoutSessionCommandService = services["checkout_session_command_service"]
    qry: CheckoutSessionQueryService = services["checkout_session_query_service"]
    return cmd, qry


def _iso_to_dt(s: Optional[str]) -> Optional[dt.datetime]:
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return dt.datetime.fromisoformat(s)
    except Exception:
        raise ValueError("expires_at debe ser ISO8601, ej: '2025-08-22T17:30:00Z'")


def _require(json: Dict[str, Any], field: str, type_=None):
    if field not in json:
        raise ValueError(f"'{field}' es requerido")
    val = json[field]
    if type_ and not isinstance(val, type_):
        raise ValueError(f"'{field}' debe ser {type_.__name__}")
    return val


def _optional(json: Dict[str, Any], field: str, type_=None, default=None):
    if field not in json:
        return default
    val = json[field]
    if type_ and val is not None and not isinstance(val, type_):
        raise ValueError(f"'{field}' debe ser {type_.__name__} o null")
    return val


def _entity_to_dict(e) -> Dict[str, Any]:
    return {
        "id": e.id,
        "order_id": e.order_id,
        "provider_session_id": e.provider_session_id,
        "init_url": e.init_url,
        "sandbox_url": e.sandbox_url,
        "expires_at": e.expires_at.isoformat() if e.expires_at else None,
        "created_at": e.created_at.isoformat() if getattr(e, "created_at", None) else None,
    }


# --------------------------
# Blueprint factory
# --------------------------
def create_checkout_session_blueprint(url_prefix: str = "/checkout/sessions") -> Blueprint:
    """
    Endpoints de interfaz para administrar Checkout Sessions (ej. Checkout Pro).
    Usa services desde current_app.config["services"] (inyectados por tu container).
    """
    bp = Blueprint("checkout_sessions", __name__)

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True), 200

    # CREATE (simple)
    # POST /checkout/sessions
    # body: {order_id:int, provider_session_id:str, init_url?:str, sandbox_url?:str, expires_at?:ISO8601}
    @bp.route("", methods=["POST"])
    def create():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            order_id = _require(body, "order_id", int)
            provider_session_id = _require(body, "provider_session_id", str)
            init_url = _optional(body, "init_url", str)
            sandbox_url = _optional(body, "sandbox_url", str)
            expires_at = _iso_to_dt(_optional(body, "expires_at", str))
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.create(
            order_id=order_id,
            provider_session_id=provider_session_id,
            init_url=init_url,
            sandbox_url=sandbox_url,
            expires_at=expires_at,
        )
        return jsonify(ok=True, data=_entity_to_dict(entity)), 201

    # CREATE OR REPLACE (idempotente por orden)
    # PUT /checkout/sessions/create-or-replace
    # body: {order_id, provider_session_id, init_url?, sandbox_url?, expires_at?, expire_previous?:bool=true}
    @bp.route("/create-or-replace", methods=["PUT"])
    def create_or_replace():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            order_id = _require(body, "order_id", int)
            provider_session_id = _require(body, "provider_session_id", str)
            init_url = _optional(body, "init_url", str)
            sandbox_url = _optional(body, "sandbox_url", str)
            expires_at = _iso_to_dt(_optional(body, "expires_at", str))
            expire_previous = bool(_optional(body, "expire_previous", default=True))
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.create_or_replace_for_order(
            order_id=order_id,
            provider_session_id=provider_session_id,
            init_url=init_url,
            sandbox_url=sandbox_url,
            expires_at=expires_at,
            expire_previous=expire_previous,
        )
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # UPDATE URLS/EXPIRATION por provider_session_id (útil si MP devuelve nuevas URLs/expiración)
    # PATCH /checkout/sessions/<provider_session_id>
    # body: {init_url?:str, sandbox_url?:str, expires_at?:ISO8601}
    @bp.route("/<string:provider_session_id>", methods=["PATCH"])
    def update_urls(provider_session_id: str):
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            init_url = _optional(body, "init_url", str)
            sandbox_url = _optional(body, "sandbox_url", str)
            expires_at = _iso_to_dt(_optional(body, "expires_at", str))
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.update_urls_by_provider_session_id(
            provider_session_id=provider_session_id,
            init_url=init_url,
            sandbox_url=sandbox_url,
            expires_at=expires_at,
        )
        if not entity:
            return jsonify(ok=False, error="checkout_session no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # EXPIRE por provider_session_id
    # POST /checkout/sessions/<provider_session_id>/expire
    @bp.route("/<string:provider_session_id>/expire", methods=["POST"])
    def expire(provider_session_id: str):
        cmd, _ = _get_services()
        entity = cmd.expire_by_provider_session_id(provider_session_id)
        if not entity:
            return jsonify(ok=False, error="checkout_session no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # DELETE por id (hard delete)
    # DELETE /checkout/sessions/<id>
    @bp.route("/<int:id_>", methods=["DELETE"])
    def delete(id_: int):
        cmd, _ = _get_services()
        ok = cmd.delete(id_)
        if not ok:
            return jsonify(ok=False, error="checkout_session no encontrado"), 404
        return jsonify(ok=True), 200

    # -------------- QUERIES --------------

    # GET /checkout/sessions/<id>
    @bp.route("/id/<int:id_>", methods=["GET"])
    def get_by_id(id_: int):
        _, qry = _get_services()
        entity = qry.get_by_id(id_)
        if not entity:
            return jsonify(ok=False, error="checkout_session no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /checkout/sessions/by-provider/<provider_session_id>
    @bp.route("/by-provider/<string:provider_session_id>", methods=["GET"])
    def get_by_provider(provider_session_id: str):
        _, qry = _get_services()
        entity = qry.get_by_provider_session_id(provider_session_id)
        if not entity:
            return jsonify(ok=False, error="checkout_session no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /checkout/sessions/by-order/<order_id>?only_active=true|false
    @bp.route("/by-order/<int:order_id>", methods=["GET"])
    def list_by_order(order_id: int):
        _, qry = _get_services()
        only_active = (request.args.get("only_active", "false").lower() == "true")
        items = qry.list_by_order(order_id=order_id, only_active=only_active)
        return jsonify(ok=True, data=[_entity_to_dict(x) for x in items]), 200

    bp.url_prefix = url_prefix
    return bp
