from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request, current_app

from payment.provider.provider_customer.domain.value_objects.enums import (
    ProviderEnum, EnvEnum, ProviderCustomerStatus
)
from payment.provider.provider_customer.domain.entities.provider_customer import (
    ProviderCustomerData
)

# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────
def _get_services():
    services = current_app.config.get("services") or {}
    cmd = services["provider_customer_command_service"]
    qry = services["provider_customer_query_service"]
    return cmd, qry


def _require(obj: Dict[str, Any], field: str):
    if field not in obj:
        raise ValueError(f"'{field}' es requerido")
    return obj[field]


def _optional(obj: Dict[str, Any], field: str, default=None):
    return obj[field] if field in obj else default


def _as_enum(value: Any, enum_cls):
    if isinstance(value, enum_cls):
        return value
    s = str(value)
    try:
        return enum_cls(s)
    except Exception:
        # tolerante a mayúsc/minúsc
        for e in enum_cls:
            if e.value.lower() == s.lower():
                return e
        raise ValueError(f"valor inválido para {enum_cls.__name__}: {value}")


def _entity_to_public_dict(e: ProviderCustomerData) -> Dict[str, Any]:
    if hasattr(e, "to_dict") and callable(getattr(e, "to_dict")):
        return e.to_dict()
    # Fallback
    return {
        "id": getattr(e, "id", None),
        "party_id": getattr(e, "party_id", None),
        "provider": e.provider.value if isinstance(e.provider, ProviderEnum) else str(getattr(e, "provider", "")),
        "env": e.env.value if isinstance(e.env, EnvEnum) else str(getattr(e, "env", "")),
        "provider_customer_id": getattr(e, "provider_customer_id", None),
        "status": e.status.value if isinstance(e.status, ProviderCustomerStatus) else str(getattr(e, "status", "")),
        "created_at": getattr(e, "created_at", None).isoformat() if getattr(e, "created_at", None) else None,
        "updated_at": getattr(e, "updated_at", None).isoformat() if getattr(e, "updated_at", None) else None,
    }


# ────────────────────────────────────────────────────────────
# Blueprint factory
# ────────────────────────────────────────────────────────────
def create_provider_customer_blueprint(url_prefix: str = "/provider-customers") -> Blueprint:
    """
    Controller HTTP para Provider Customers.

    Requiere en current_app.config['services']:
      - provider_customer_command_service : ProviderCustomerCommandService
      - provider_customer_query_service   : ProviderCustomerQueryService
    """
    bp = Blueprint("provider_customers", __name__)

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True), 200

    # ──────────────
    # QUERIES
    # ──────────────
    # GET /provider-customers/id/<id>
    @bp.route("/id/<int:pc_id>", methods=["GET"])
    def get_by_id(pc_id: int):
        _, qry = _get_services()
        entity = qry.get_by_id(pc_id)
        if not entity:
            return jsonify(ok=False, error="provider_customer no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # GET /provider-customers/by-party-provider-env?party_id=&provider=&env=
    @bp.route("/by-party-provider-env", methods=["GET"])
    def get_by_party_provider_env():
        _, qry = _get_services()
        try:
            party_id = int(_require(request.args, "party_id"))
            provider = _as_enum(_require(request.args, "provider"), ProviderEnum)
            env = _as_enum(_require(request.args, "env"), EnvEnum)
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        entity = qry.get_by_party_provider_env(party_id, provider, env)
        if not entity:
            return jsonify(ok=False, error="provider_customer no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # GET /provider-customers/by-external?provider=&env=&provider_customer_id=
    @bp.route("/by-external", methods=["GET"])
    def get_by_provider_external_id():
        _, qry = _get_services()
        try:
            provider = _as_enum(_require(request.args, "provider"), ProviderEnum)
            env = _as_enum(_require(request.args, "env"), EnvEnum)
            provider_customer_id = str(_require(request.args, "provider_customer_id"))
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        entity = qry.get_by_provider_external_id(provider, env, provider_customer_id)
        if not entity:
            return jsonify(ok=False, error="provider_customer no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # GET /provider-customers/by-party/<party_id>
    @bp.route("/by-party/<int:party_id>", methods=["GET"])
    def list_by_party(party_id: int):
        _, qry = _get_services()
        items = qry.list_by_party(party_id)
        return jsonify(ok=True, data=[_entity_to_public_dict(i) for i in items]), 200

    # GET /provider-customers?limit=100&offset=0
    @bp.route("", methods=["GET"])
    def list_all():
        _, qry = _get_services()
        try:
            limit = int(request.args.get("limit", 100))
            offset = int(request.args.get("offset", 0))
        except Exception:
            return jsonify(ok=False, error="limit/offset inválidos"), 400
        items = qry.list_all(limit=limit, offset=offset)
        return jsonify(ok=True, data=[_entity_to_public_dict(i) for i in items]), 200

    # ──────────────
    # COMMANDS
    # ──────────────
    # POST /provider-customers
    # body: {party_id, provider, env, provider_customer_id, status?}
    @bp.route("", methods=["POST"])
    def create_pc():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            party_id = int(_require(body, "party_id"))
            provider = _as_enum(_require(body, "provider"), ProviderEnum)
            env = _as_enum(_require(body, "env"), EnvEnum)
            provider_customer_id = str(_require(body, "provider_customer_id"))
            status = _as_enum(_optional(body, "status", ProviderCustomerStatus.ACTIVE.value), ProviderCustomerStatus)
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        entity = cmd.create(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_customer_id=provider_customer_id,
            status=status,
        )
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 201

    # PUT /provider-customers/id/<id>
    @bp.route("/id/<int:pc_id>", methods=["PUT"])
    def update_pc(pc_id: int):
        cmd, qry = _get_services()
        current = qry.get_by_id(pc_id)
        if not current:
            return jsonify(ok=False, error="provider_customer no encontrado"), 404

        body = request.get_json(silent=True) or {}
        try:
            party_id = int(_optional(body, "party_id", current.party_id))
            provider = _as_enum(_optional(body, "provider",
                                          current.provider.value if isinstance(current.provider, ProviderEnum)
                                          else current.provider), ProviderEnum)
            env = _as_enum(_optional(body, "env",
                                     current.env.value if isinstance(current.env, EnvEnum)
                                     else current.env), EnvEnum)
            provider_customer_id = str(_optional(body, "provider_customer_id", current.provider_customer_id))
            status = _as_enum(_optional(body, "status",
                                        current.status.value if isinstance(current.status, ProviderCustomerStatus)
                                        else current.status), ProviderCustomerStatus)
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        updated = cmd.update(
            id_=pc_id,
            party_id=party_id,
            provider=provider,
            env=env,
            provider_customer_id=provider_customer_id,
            status=status,
        )
        return jsonify(ok=True, data=_entity_to_public_dict(updated)), 200

    # PUT /provider-customers/upsert-by-party
    # body: {party_id, provider, env, provider_customer_id, status?}
    @bp.route("/upsert-by-party", methods=["PUT"])
    def upsert_by_party():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            party_id = int(_require(body, "party_id"))
            provider = _as_enum(_require(body, "provider"), ProviderEnum)
            env = _as_enum(_require(body, "env"), EnvEnum)
            provider_customer_id = str(_require(body, "provider_customer_id"))
            status = _as_enum(_optional(body, "status", ProviderCustomerStatus.ACTIVE.value), ProviderCustomerStatus)
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        entity = cmd.upsert_by_party(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_customer_id=provider_customer_id,
            status=status,
        )
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # PATCH /provider-customers/set-status
    # body: {party_id, provider, env, status}
    @bp.route("/set-status", methods=["PATCH"])
    def set_status():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            party_id = int(_require(body, "party_id"))
            provider = _as_enum(_require(body, "provider"), ProviderEnum)
            env = _as_enum(_require(body, "env"), EnvEnum)
            status = _as_enum(_require(body, "status"), ProviderCustomerStatus)
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        entity = cmd.set_status(party_id, provider, env, status)
        if not entity:
            return jsonify(ok=False, error="provider_customer no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # DELETE /provider-customers/id/<id>
    @bp.route("/id/<int:pc_id>", methods=["DELETE"])
    def delete_pc(pc_id: int):
        cmd, _ = _get_services()
        ok = cmd.delete(pc_id)
        if not ok:
            return jsonify(ok=False, error="provider_customer no encontrado"), 404
        return jsonify(ok=True), 200

    bp.url_prefix = url_prefix
    return bp
