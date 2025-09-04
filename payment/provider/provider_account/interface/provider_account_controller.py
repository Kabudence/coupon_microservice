from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List, Union

from flask import Blueprint, jsonify, request, current_app

from payment.provider.provider_account.domain.entities.provider_account import ProviderAccountData, \
    ProviderAccountStatus, EnvKind, ProviderKind


# Los services se obtienen desde current_app.config["services"],
# no es necesario importarlos directamente aquí.


# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────
def _get_services():
    services = current_app.config.get("services") or {}
    cmd = services["provider_account_command_service"]
    qry = services["provider_account_query_service"]
    return cmd, qry


def _require(obj: Dict[str, Any], field: str):
    if field not in obj:
        raise ValueError(f"'{field}' es requerido")
    return obj[field]


def _optional(obj: Dict[str, Any], field: str, default=None):
    return obj[field] if field in obj else default


def _as_enum(value: Any, enum_cls):
    """
    Acepta instancia Enum o string (case-insensitive por .value).
    """
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


def _entity_to_public_dict(e: ProviderAccountData) -> Dict[str, Any]:
    """
    NO exponer secret_json_enc en respuestas públicas.
    """
    # Usar to_dict si existe
    if hasattr(e, "to_dict") and callable(getattr(e, "to_dict")):
        data = e.to_dict()
        # Redactar secrets si vinieran
        if "secret_json_enc" in data:
            data["secret_json_enc"] = None
            data["has_secret"] = True
        else:
            data["has_secret"] = False
        return data

    # Fallback genérico
    return {
        "id": getattr(e, "id", None),
        "party_id": getattr(e, "party_id", None),
        "provider": getattr(e, "provider", None) if not isinstance(getattr(e, "provider", None), ProviderKind)
                    else getattr(e, "provider").value,
        "env": getattr(e, "env", None) if not isinstance(getattr(e, "env", None), EnvKind)
                else getattr(e, "env").value,
        "provider_account_id": getattr(e, "provider_account_id", None),
        "public_key": getattr(e, "public_key", None),
        "status": getattr(e, "status", None) if not isinstance(getattr(e, "status", None), ProviderAccountStatus)
                  else getattr(e, "status").value,
        "has_secret": bool(getattr(e, "secret_json_enc", None)),
        "created_at": getattr(e, "created_at", None).isoformat() if getattr(e, "created_at", None) else None,
        "updated_at": getattr(e, "updated_at", None).isoformat() if getattr(e, "updated_at", None) else None,
    }


# ────────────────────────────────────────────────────────────
# Blueprint factory
# ────────────────────────────────────────────────────────────
def create_provider_account_blueprint(url_prefix: str = "/provider-accounts") -> Blueprint:
    """
    Controller HTTP para Provider Accounts.

    Requiere en current_app.config['services']:
      - provider_account_command_service : ProviderAccountCommandService
      - provider_account_query_service   : ProviderAccountQueryService
    """
    bp = Blueprint("provider_accounts", __name__)

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True), 200

    # ──────────────
    # QUERIES
    # ──────────────
    # GET /provider-accounts/id/<id>
    @bp.route("/id/<int:acc_id>", methods=["GET"])
    def get_by_id(acc_id: int):
        _, qry = _get_services()
        entity = qry.get_by_id(acc_id)
        if not entity:
            return jsonify(ok=False, error="provider_account no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # GET /provider-accounts/unique?provider=mercadopago&env=test&provider_account_id=2627...
    @bp.route("/unique", methods=["GET"])
    def get_by_unique():
        _, qry = _get_services()
        try:
            provider = _as_enum(_require(request.args, "provider"), ProviderKind)
            env = _as_enum(_require(request.args, "env"), EnvKind)
            provider_account_id = str(_require(request.args, "provider_account_id"))
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        entity = qry.get_by_unique(provider, env, provider_account_id)
        if not entity:
            return jsonify(ok=False, error="provider_account no encontrado"), 404
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # GET /provider-accounts/by-party/<party_id>?only_active=true
    @bp.route("/by-party/<int:party_id>", methods=["GET"])
    def list_by_party(party_id: int):
        _, qry = _get_services()
        only_active = request.args.get("only_active", "false").lower() in ("1", "true", "yes")
        items = qry.list_by_party(party_id, only_active=only_active)
        return jsonify(ok=True, data=[_entity_to_public_dict(i) for i in items]), 200

    # GET /provider-accounts/by-party-env/<party_id>?env=test&provider=mercadopago&only_active=true
    @bp.route("/by-party-env/<int:party_id>", methods=["GET"])
    def list_by_party_env(party_id: int):
        _, qry = _get_services()
        try:
            env = _as_enum(_require(request.args, "env"), EnvKind)
            provider_arg = request.args.get("provider")
            provider = _as_enum(provider_arg, ProviderKind) if provider_arg else None
            only_active = request.args.get("only_active", "false").lower() in ("1", "true", "yes")
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        items = qry.list_by_party_env(
            party_id=party_id,
            env=env,
            provider=provider,
            only_active=only_active,
        )
        return jsonify(ok=True, data=[_entity_to_public_dict(i) for i in items]), 200

    # GET /provider-accounts/find-active?party_id=..&provider=..&env=..
    @bp.route("/find-active", methods=["GET"])
    def find_active_for_party():
        _, qry = _get_services()
        try:
            party_id = int(_require(request.args, "party_id"))
            provider = _as_enum(_require(request.args, "provider"), ProviderKind)
            env = _as_enum(_require(request.args, "env"), EnvKind)
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        entity = qry.find_active_account_for_party(party_id, provider, env)
        if not entity:
            return jsonify(ok=False, error="no hay cuenta activa para ese party/provider/env"), 404
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    # GET /provider-accounts/stats/by-provider-env
    @bp.route("/stats/by-provider-env", methods=["GET"])
    def stats_by_provider_env():
        _, qry = _get_services()
        stats = qry.stats_count_by_provider_env()
        return jsonify(ok=True, data=stats), 200

    # GET /provider-accounts/dump/<id>  (debug)
    @bp.route("/dump/<int:acc_id>", methods=["GET"])
    def dump_model(acc_id: int):
        _, qry = _get_services()
        model_dict = qry.dump_model(acc_id)
        if not model_dict:
            return jsonify(ok=False, error="provider_account no encontrado"), 404
        # Por seguridad, no devolvemos secrets en dump tampoco
        if "secret_json_enc" in model_dict:
            model_dict["secret_json_enc"] = None
            model_dict["has_secret"] = True
        return jsonify(ok=True, data=model_dict), 200

    # ──────────────
    # COMMANDS
    # ──────────────
    # POST /provider-accounts
    # body: {party_id, provider, env, provider_account_id, public_key?, secret_json_enc?, status?}
    @bp.route("", methods=["POST"])
    def create_account():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            party_id = int(_require(body, "party_id"))
            provider = _as_enum(_require(body, "provider"), ProviderKind)
            env = _as_enum(_require(body, "env"), EnvKind)
            provider_account_id = str(_require(body, "provider_account_id"))
            public_key = _optional(body, "public_key")
            secret_json_enc: Optional[Union[str, Dict[str, Any]]] = _optional(body, "secret_json_enc")
            status = _as_enum(_optional(body, "status", ProviderAccountStatus.ACTIVE.value), ProviderAccountStatus)
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        entity = cmd.create(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_account_id=provider_account_id,
            public_key=public_key,
            secret_json_enc=secret_json_enc,
            status=status,
        )
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 201

    # PUT /provider-accounts/id/<id>
    @bp.route("/id/<int:acc_id>", methods=["PUT"])
    def update_account(acc_id: int):
        cmd, qry = _get_services()
        current = qry.get_by_id(acc_id)
        if not current:
            return jsonify(ok=False, error="provider_account no encontrado"), 404

        body = request.get_json(silent=True) or {}
        try:
            party_id = int(_optional(body, "party_id", current.party_id))
            provider = _as_enum(_optional(body, "provider",
                                          current.provider.value if isinstance(current.provider, ProviderKind)
                                          else current.provider), ProviderKind)
            env = _as_enum(_optional(body, "env",
                                     current.env.value if isinstance(current.env, EnvKind)
                                     else current.env), EnvKind)
            provider_account_id = str(_optional(body, "provider_account_id", current.provider_account_id))
            public_key = _optional(body, "public_key", current.public_key)
            secret_json_enc: Optional[Union[str, Dict[str, Any]]] = _optional(body, "secret_json_enc",
                                                                              getattr(current, "secret_json_enc", None))
            status = _as_enum(_optional(body, "status",
                                        current.status.value if isinstance(current.status, ProviderAccountStatus)
                                        else current.status), ProviderAccountStatus)
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        updated = cmd.update(
            id_=acc_id,
            party_id=party_id,
            provider=provider,
            env=env,
            provider_account_id=provider_account_id,
            public_key=public_key,
            secret_json_enc=secret_json_enc,
            status=status,
        )
        return jsonify(ok=True, data=_entity_to_public_dict(updated)), 200

    # DELETE /provider-accounts/id/<id>
    @bp.route("/id/<int:acc_id>", methods=["DELETE"])
    def delete_account(acc_id: int):
        cmd, _ = _get_services()
        ok = cmd.delete(acc_id)
        if not ok:
            return jsonify(ok=False, error="provider_account no encontrado"), 404
        return jsonify(ok=True), 200

    # PATCH /provider-accounts/id/<id>/enable
    @bp.route("/id/<int:acc_id>/enable", methods=["PATCH"])
    def enable_account(acc_id: int):
        cmd, _ = _get_services()
        ok = cmd.enable(acc_id)
        if not ok:
            return jsonify(ok=False, error="provider_account no encontrado"), 404
        return jsonify(ok=True), 200

    # PATCH /provider-accounts/id/<id>/disable
    @bp.route("/id/<int:acc_id>/disable", methods=["PATCH"])
    def disable_account(acc_id: int):
        cmd, _ = _get_services()
        ok = cmd.disable(acc_id)
        if not ok:
            return jsonify(ok=False, error="provider_account no encontrado"), 404
        return jsonify(ok=True), 200

    # PATCH /provider-accounts/id/<id>/rotate-secrets
    # body: { new_secret_json_enc: str|object }
    @bp.route("/id/<int:acc_id>/rotate-secrets", methods=["PATCH"])
    def rotate_secrets(acc_id: int):
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            new_secret_json_enc = _require(body, "new_secret_json_enc")
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        ok = cmd.rotate_secrets(acc_id, new_secret_json_enc)
        if not ok:
            return jsonify(ok=False, error="provider_account no encontrado"), 404
        return jsonify(ok=True), 200

    # PUT /provider-accounts/upsert
    # body: igual a create (usa tu índice único provider+env+provider_account_id)
    @bp.route("/upsert", methods=["PUT"])
    def upsert_account():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            party_id = int(_require(body, "party_id"))
            provider = _as_enum(_require(body, "provider"), ProviderKind)
            env = _as_enum(_require(body, "env"), EnvKind)
            provider_account_id = str(_require(body, "provider_account_id"))
            public_key = _optional(body, "public_key")
            secret_json_enc: Optional[Union[str, Dict[str, Any]]] = _optional(body, "secret_json_enc")
            status = _as_enum(_optional(body, "status", ProviderAccountStatus.ACTIVE.value), ProviderAccountStatus)
        except Exception as e:
            return jsonify(ok=False, error=f"payload inválido: {e}"), 400

        entity = cmd.upsert(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_account_id=provider_account_id,
            public_key=public_key,
            secret_json_enc=secret_json_enc,
            status=status,
        )
        return jsonify(ok=True, data=_entity_to_public_dict(entity)), 200

    bp.url_prefix = url_prefix
    return bp
