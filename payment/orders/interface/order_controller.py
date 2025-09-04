from __future__ import annotations

import datetime as dt
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Tuple, List

from flask import Blueprint, jsonify, request, current_app

from payment.orders.application.command.order_command_service import OrderCommandService
from payment.orders.application.queries.order_query_service import OrderQueryService
from payment.orders.domain.value_objects.enums import OrderStatus, PaymentFlow
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum


# --------------------------
# Helpers (parse / utils)
# --------------------------
def _get_services() -> Tuple[OrderCommandService, OrderQueryService]:
    services = current_app.config.get("services") or {}
    cmd: OrderCommandService = services["order_command_service"]
    qry: OrderQueryService = services["order_query_service"]
    return cmd, qry


def _parse_decimal(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"'{field}' debe ser un número (Decimal/float/str) válido")


def _iso_to_dt(s: Optional[str]) -> Optional[dt.datetime]:
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return dt.datetime.fromisoformat(s)
    except Exception:
        raise ValueError(f"'{s}' no es una fecha ISO8601 válida (usa, p.ej., 2025-01-31T15:04:05Z)")


def _as_enum(value: Any, enum_cls):
    if value is None:
        return None
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(str(value))
    except Exception:
        # permitir mayúsc/minúsc sin romper
        for e in enum_cls:
            if e.value.lower() == str(value).lower():
                return e
        raise ValueError(f"valor inválido para {enum_cls.__name__}: {value}")


def _require(body: Dict[str, Any], field: str):
    if field not in body:
        raise ValueError(f"'{field}' es requerido")
    return body[field]


def _optional(body: Dict[str, Any], field: str, default=None):
    return body[field] if field in body else default


def _entity_to_dict(e) -> Dict[str, Any]:
    if hasattr(e, "to_dict") and callable(getattr(e, "to_dict")):
        return e.to_dict()
    # fallback genérico
    return {
        "id": getattr(e, "id", None),
        "buyer_party_id": getattr(e, "buyer_party_id", None),
        "seller_party_id": getattr(e, "seller_party_id", None),
        "amount": str(getattr(e, "amount", None)) if getattr(e, "amount", None) is not None else None,
        "currency": getattr(e, "currency", None),
        "status": getattr(e, "status", None).value if isinstance(getattr(e, "status", None), OrderStatus) else getattr(e, "status", None),
        "description": getattr(e, "description", None),
        "metadata": getattr(e, "metadata", None),
        "flow": getattr(e, "flow", None).value if isinstance(getattr(e, "flow", None), PaymentFlow) else getattr(e, "flow", None),
        "provider": getattr(e, "provider", None).value if isinstance(getattr(e, "provider", None), ProviderEnum) else getattr(e, "provider", None),
        "env": getattr(e, "env", None).value if isinstance(getattr(e, "env", None), EnvEnum) else getattr(e, "env", None),
        "provider_account_id": getattr(e, "provider_account_id", None),
        "provider_payment_id": getattr(e, "provider_payment_id", None),
        "idempotency_key": getattr(e, "idempotency_key", None),
        "payment_type": getattr(e, "payment_type", None),
        "method_brand": getattr(e, "method_brand", None),
        "method_last_four": getattr(e, "method_last_four", None),
        "paid_at": getattr(e, "paid_at", None).isoformat() if getattr(e, "paid_at", None) else None,
        "created_at": getattr(e, "created_at", None).isoformat() if getattr(e, "created_at", None) else None,
        "updated_at": getattr(e, "updated_at", None).isoformat() if getattr(e, "updated_at", None) else None,
    }


# --------------------------
# Blueprint factory
# --------------------------
def create_order_blueprint(url_prefix: str = "/orders") -> Blueprint:
    """
    Controller (capa de interfaz) para Orders.
    Usa services inyectados vía current_app.config['services'].
    """
    bp = Blueprint("orders", __name__)

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True), 200

    # ---------------------------------
    # Commands
    # ---------------------------------

    # POST /orders
    # body: {buyer_party_id, seller_party_id, amount, currency?, description?, metadata?}
    @bp.route("", methods=["POST"])
    def create_order():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            buyer_party_id = int(_require(body, "buyer_party_id"))
            seller_party_id = int(_require(body, "seller_party_id"))
            amount = _parse_decimal(_require(body, "amount"), "amount")
            currency = str(_optional(body, "currency", "PEN"))
            description = _optional(body, "description")
            metadata = _optional(body, "metadata", {}) or {}
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.create(
            buyer_party_id=buyer_party_id,
            seller_party_id=seller_party_id,
            amount=amount,
            currency=currency,
            description=description,
            metadata=metadata,
        )
        return jsonify(ok=True, data=_entity_to_dict(entity)), 201

    # PATCH /orders/<id>/checkout-context
    # body: {flow, provider, env?, provider_account_id?, idempotency_key?, mark_processing?:bool, extra_metadata?:{}}
    @bp.route("/<int:order_id>/checkout-context", methods=["PATCH"])
    def set_checkout_context(order_id: int):
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            flow = _as_enum(_require(body, "flow"), PaymentFlow)
            provider = _as_enum(_require(body, "provider"), ProviderEnum)
            env = _as_enum(_optional(body, "env", EnvEnum.TEST.value), EnvEnum)
            provider_account_id = _optional(body, "provider_account_id")
            if provider_account_id is not None:
                provider_account_id = int(provider_account_id)
            idempotency_key = _optional(body, "idempotency_key")
            mark_processing = bool(_optional(body, "mark_processing", True))
            extra_metadata = _optional(body, "extra_metadata", {}) or {}
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.set_checkout_context(
            order_id=order_id,
            flow=flow,
            provider=provider,
            env=env,
            provider_account_id=provider_account_id,
            idempotency_key=idempotency_key,
            mark_processing=mark_processing,
            extra_metadata=extra_metadata,
        )
        if not entity:
            return jsonify(ok=False, error="order no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # POST /orders/<id>/mark-paid
    # body: {provider_payment_id, payment_type?, method_brand?, method_last_four?, paid_at?:ISO, extra_metadata?:{}}
    @bp.route("/<int:order_id>/mark-paid", methods=["POST"])
    def mark_paid(order_id: int):
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            provider_payment_id = str(_require(body, "provider_payment_id"))
            payment_type = _optional(body, "payment_type")
            method_brand = _optional(body, "method_brand")
            method_last_four = _optional(body, "method_last_four")
            paid_at = _iso_to_dt(_optional(body, "paid_at"))
            extra_metadata = _optional(body, "extra_metadata", {}) or {}
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.mark_paid(
            order_id=order_id,
            provider_payment_id=provider_payment_id,
            payment_type=payment_type,
            method_brand=method_brand,
            method_last_four=method_last_four,
            paid_at=paid_at,
            extra_metadata=extra_metadata,
        )
        if not entity:
            return jsonify(ok=False, error="order no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # POST /orders/<id>/mark-failed
    # body: {error_code?, error_message?, extra_metadata?:{}}
    @bp.route("/<int:order_id>/mark-failed", methods=["POST"])
    def mark_failed(order_id: int):
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        error_code = _optional(body, "error_code")
        error_message = _optional(body, "error_message")
        extra_metadata = _optional(body, "extra_metadata", {}) or {}

        entity = cmd.mark_failed(
            order_id=order_id,
            error_code=error_code,
            error_message=error_message,
            extra_metadata=extra_metadata,
        )
        if not entity:
            return jsonify(ok=False, error="order no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # POST /orders/<id>/cancel
    # body: {reason?}
    @bp.route("/<int:order_id>/cancel", methods=["POST"])
    def cancel(order_id: int):
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        reason = _optional(body, "reason")
        entity = cmd.cancel(order_id, reason=reason)
        if not entity:
            return jsonify(ok=False, error="order no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # ---------------------------------
    # Queries
    # ---------------------------------

    # GET /orders/id/<id>
    @bp.route("/id/<int:order_id>", methods=["GET"])
    def get_by_id(order_id: int):
        _, qry = _get_services()
        entity = qry.get_by_id(order_id)
        if not entity:
            return jsonify(ok=False, error="order no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /orders/by-provider?provider=mercadopago&env=test&provider_payment_id=123
    @bp.route("/by-provider", methods=["GET"])
    def get_by_provider_payment():
        _, qry = _get_services()
        try:
            provider = _as_enum(request.args.get("provider"), ProviderEnum)
            env = _as_enum(request.args.get("env", EnvEnum.TEST.value), EnvEnum)
            provider_payment_id = request.args.get("provider_payment_id")
            if not provider_payment_id:
                raise ValueError("'provider_payment_id' es requerido")
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = qry.get_by_provider_payment(provider, env, provider_payment_id)
        if not entity:
            return jsonify(ok=False, error="order no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /orders/by-idempotency?provider=mercadopago&env=test&idempotency_key=abc
    @bp.route("/by-idempotency", methods=["GET"])
    def get_by_idempotency():
        _, qry = _get_services()
        try:
            provider = _as_enum(request.args.get("provider"), ProviderEnum)
            env = _as_enum(request.args.get("env", EnvEnum.TEST.value), EnvEnum)
            idem = request.args.get("idempotency_key")
            if not idem:
                raise ValueError("'idempotency_key' es requerido")
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = qry.get_by_idempotency(provider, env, idem)
        if not entity:
            return jsonify(ok=False, error="order no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /orders/by-buyer/<buyer_party_id>?status=pending&limit=50&offset=0
    @bp.route("/by-buyer/<int:buyer_party_id>", methods=["GET"])
    def list_by_buyer(buyer_party_id: int):
        _, qry = _get_services()
        status_raw = request.args.get("status")
        status = _as_enum(status_raw, OrderStatus) if status_raw else None
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        items = qry.list_by_buyer(buyer_party_id, status=status, limit=limit, offset=offset)
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    # GET /orders/by-seller/<seller_party_id>?status=paid&limit=50&offset=0
    @bp.route("/by-seller/<int:seller_party_id>", methods=["GET"])
    def list_by_seller(seller_party_id: int):
        _, qry = _get_services()
        status_raw = request.args.get("status")
        status = _as_enum(status_raw, OrderStatus) if status_raw else None
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        items = qry.list_by_seller(seller_party_id, status=status, limit=limit, offset=offset)
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    # GET /orders/by-status/<status>?limit=50&offset=0
    @bp.route("/by-status/<string:status>", methods=["GET"])
    def list_by_status(status: str):
        _, qry = _get_services()
        try:
            status_enum = _as_enum(status, OrderStatus)
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        items = qry.list_by_status(status_enum, limit=limit, offset=offset)
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    bp.url_prefix = url_prefix
    return bp
