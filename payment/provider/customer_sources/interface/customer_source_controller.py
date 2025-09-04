from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List

from flask import Blueprint, jsonify, request, current_app

from payment.provider.customer_sources.application.command.payment_source_command_service import \
    PaymentSourceCommandService
from payment.provider.customer_sources.application.queries.payment_source_query_service import PaymentSourceQueryService
from payment.provider.customer_sources.domain.entities.payment_source import PaymentSourceData
from payment.provider.customer_sources.domain.valueobjects.enums import PaymentSourceStatus
from payment.provider.provider_customer.domain.value_objects.enums import EnvEnum


# --------------------------
# Helpers
# --------------------------
def _get_services() -> Tuple[PaymentSourceCommandService, PaymentSourceQueryService]:
    services = current_app.config.get("services") or {}
    cmd: PaymentSourceCommandService = services["payment_source_command_service"]
    qry: PaymentSourceQueryService = services["payment_source_query_service"]
    return cmd, qry


def _as_enum(value: Any, enum_cls):
    if value is None:
        raise ValueError(f"valor requerido para {enum_cls.__name__}")
    if isinstance(value, enum_cls):
        return value
    s = str(value)
    try:
        return enum_cls(s)
    except Exception:
        for e in enum_cls:
            if e.value.lower() == s.lower():
                return e
        raise ValueError(f"valor inválido para {enum_cls.__name__}: {value}")


def _require(body: Dict[str, Any], field: str):
    if field not in body:
        raise ValueError(f"'{field}' es requerido")
    return body[field]


def _optional(body: Dict[str, Any], field: str, default=None):
    return body[field] if field in body else default


def _entity_to_dict(e: PaymentSourceData) -> Dict[str, Any]:
    # Si tu entidad ya tiene to_dict(), úsala.
    if hasattr(e, "to_dict") and callable(getattr(e, "to_dict")):
        return e.to_dict()
    return {
        "id": getattr(e, "id", None),
        "provider_customer_pk": getattr(e, "provider_customer_pk", None),
        "provider": getattr(e, "provider", None),
        "env": getattr(e, "env", None) if not isinstance(getattr(e, "env", None), EnvEnum)
               else getattr(e, "env").value,
        "provider_source_id": getattr(e, "provider_source_id", None),
        "source_type": getattr(e, "source_type", None),
        "brand": getattr(e, "brand", None),
        "last_four": getattr(e, "last_four", None),
        "exp_month": getattr(e, "exp_month", None),
        "exp_year": getattr(e, "exp_year", None),
        "holder_name": getattr(e, "holder_name", None),
        "status": getattr(e, "status", None) if not isinstance(getattr(e, "status", None), PaymentSourceStatus)
                  else getattr(e, "status").value,
        "created_at": getattr(e, "created_at", None).isoformat() if getattr(e, "created_at", None) else None,
        "updated_at": getattr(e, "updated_at", None).isoformat() if getattr(e, "updated_at", None) else None,
    }


# --------------------------
# Blueprint factory
# --------------------------
def create_payment_source_blueprint(url_prefix: str = "/payment-sources") -> Blueprint:
    """
    Controller HTTP para payment_sources.
    Requiere en current_app.config['services']:
      - payment_source_command_service
      - payment_source_query_service
    """
    bp = Blueprint("payment_sources", __name__)

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True), 200

    # --------------------------
    # Queries
    # --------------------------
    # GET /payment-sources/id/<id>
    @bp.route("/id/<int:ps_id>", methods=["GET"])
    def get_by_id(ps_id: int):
        _, qry = _get_services()
        entity = qry.get_by_id(ps_id)
        if not entity:
            return jsonify(ok=False, error="payment_source no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /payment-sources/by-customer-source?provider_customer_pk=..&provider_source_id=..
    @bp.route("/by-customer-source", methods=["GET"])
    def get_by_customer_and_source_id():
        _, qry = _get_services()
        try:
            provider_customer_pk = int(_require(request.args, "provider_customer_pk"))
            provider_source_id = str(_require(request.args, "provider_source_id"))
        except ValueError as e:
            return jsonify(ok=False, error=str(e)), 400

        entity = qry.get_by_customer_and_source_id(provider_customer_pk, provider_source_id)
        if not entity:
            return jsonify(ok=False, error="payment_source no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /payment-sources/by-customer/<pk>?only_active=true
    @bp.route("/by-customer/<int:provider_customer_pk>", methods=["GET"])
    def list_by_customer(provider_customer_pk: int):
        _, qry = _get_services()
        only_active = request.args.get("only_active", "true").lower() in ("true", "1", "yes")
        items = qry.list_by_customer(provider_customer_pk, only_active=only_active)
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    # GET /payment-sources/by-customer/<pk>/cards/active
    @bp.route("/by-customer/<int:provider_customer_pk>/cards/active", methods=["GET"])
    def list_active_cards(provider_customer_pk: int):
        _, qry = _get_services()
        items = qry.list_active_cards(provider_customer_pk)
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    # GET /payment-sources/by-customer/<pk>/wallet
    @bp.route("/by-customer/<int:provider_customer_pk>/wallet", methods=["GET"])
    def get_wallet(provider_customer_pk: int):
        _, qry = _get_services()
        entity = qry.get_wallet(provider_customer_pk)
        if not entity:
            return jsonify(ok=False, error="wallet no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # --------------------------
    # Commands (genéricos)
    # --------------------------
    # POST /payment-sources
    # body: {provider_customer_pk, provider, env, provider_source_id?, source_type, brand?, last_four?, exp_month?, exp_year?, holder_name?, status?}
    @bp.route("", methods=["POST"])
    def create_payment_source():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            entity = PaymentSourceData(
                provider_customer_pk=int(_require(body, "provider_customer_pk")),
                provider=str(_require(body, "provider")),
                env=_optional(body, "env", EnvEnum.TEST.value),
                provider_source_id=_optional(body, "provider_source_id"),
                source_type=str(_require(body, "source_type")),
                brand=_optional(body, "brand"),
                last_four=_optional(body, "last_four"),
                exp_month=_optional(body, "exp_month"),
                exp_year=_optional(body, "exp_year"),
                holder_name=_optional(body, "holder_name"),
                status=_optional(body, "status", PaymentSourceStatus.ACTIVE.value),
            )
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        created = cmd.create(entity)
        return jsonify(ok=True, data=_entity_to_dict(created)), 201

    # PUT /payment-sources/id/<id>
    # body igual al create (campos opcionales)
    @bp.route("/id/<int:ps_id>", methods=["PUT"])
    def update_payment_source(ps_id: int):
        cmd, qry = _get_services()
        current = qry.get_by_id(ps_id)
        if not current:
            return jsonify(ok=False, error="payment_source no encontrado"), 404

        body = request.get_json(silent=True) or {}
        # construimos un nuevo entity con merge de valores
        updated = PaymentSourceData(
            id=current.id,
            provider_customer_pk=int(_optional(body, "provider_customer_pk", current.provider_customer_pk)),
            provider=str(_optional(body, "provider", current.provider)),
            env=_optional(body, "env", current.env.value if isinstance(current.env, EnvEnum) else current.env),
            provider_source_id=_optional(body, "provider_source_id", current.provider_source_id),
            source_type=str(_optional(body, "source_type", current.source_type)),
            brand=_optional(body, "brand", current.brand),
            last_four=_optional(body, "last_four", current.last_four),
            exp_month=_optional(body, "exp_month", current.exp_month),
            exp_year=_optional(body, "exp_year", current.exp_year),
            holder_name=_optional(body, "holder_name", current.holder_name),
            status=_optional(
                body, "status",
                current.status.value if isinstance(current.status, PaymentSourceStatus) else current.status
            ),
        )
        saved = cmd.update(updated)
        if not saved:
            return jsonify(ok=False, error="no se pudo actualizar"), 400
        return jsonify(ok=True, data=_entity_to_dict(saved)), 200

    # DELETE /payment-sources/id/<id>  (hard delete)
    @bp.route("/id/<int:ps_id>", methods=["DELETE"])
    def delete_payment_source(ps_id: int):
        cmd, _ = _get_services()
        ok = cmd.delete(ps_id)
        if not ok:
            return jsonify(ok=False, error="payment_source no encontrado"), 404
        return jsonify(ok=True), 200

    # PATCH /payment-sources/id/<id>/soft-delete
    @bp.route("/id/<int:ps_id>/soft-delete", methods=["PATCH"])
    def soft_delete_payment_source(ps_id: int):
        cmd, _ = _get_services()
        ok = cmd.soft_delete(ps_id)
        if not ok:
            return jsonify(ok=False, error="payment_source no encontrado"), 404
        return jsonify(ok=True), 200

    # --------------------------
    # Commands (upserts específicos)
    # --------------------------
    # PUT /payment-sources/upsert/card
    # body: {provider_customer_pk, provider_source_id, brand, last_four, exp_month, exp_year, holder_name?, status?}
    @bp.route("/upsert/card", methods=["PUT"])
    def upsert_card():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            entity = cmd.upsert_card(
                provider_customer_pk=int(_require(body, "provider_customer_pk")),
                provider_source_id=str(_require(body, "provider_source_id")),
                brand=str(_require(body, "brand")),
                last_four=str(_require(body, "last_four")),
                exp_month=int(_require(body, "exp_month")),
                exp_year=int(_require(body, "exp_year")),
                holder_name=_optional(body, "holder_name"),
                status=_optional(body, "status", PaymentSourceStatus.ACTIVE.value),
            )
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # PUT /payment-sources/upsert/wallet
    # body: {provider_customer_pk, holder_name?, status?}
    @bp.route("/upsert/wallet", methods=["PUT"])
    def upsert_wallet():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            entity = cmd.upsert_wallet(
                provider_customer_pk=int(_require(body, "provider_customer_pk")),
                holder_name=_optional(body, "holder_name"),
                status=_optional(body, "status", PaymentSourceStatus.ACTIVE.value),
            )
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # PUT /payment-sources/upsert/mp-card
    # body: {provider_customer_pk, env, mp_card: {...}}  (mp_card viene directo del JSON de MP /v1/customers/<id>/cards)
    @bp.route("/upsert/mp-card", methods=["PUT"])
    def upsert_from_mp_card_json():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            provider_customer_pk = int(_require(body, "provider_customer_pk"))
            env = _as_enum(_require(body, "env"), EnvEnum)
            mp_card = _require(body, "mp_card")
            if not isinstance(mp_card, dict):
                raise ValueError("'mp_card' debe ser un objeto JSON")
            entity = cmd.upsert_from_mp_card_json(
                provider_customer_pk=provider_customer_pk,
                env=env,
                mp_card=mp_card,
            )
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    bp.url_prefix = url_prefix
    return bp
