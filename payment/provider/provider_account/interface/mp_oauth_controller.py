# payment/provider/provider_account/interface/mp_oauth_controller.py
from __future__ import annotations

import os, base64, json, time
from urllib.parse import urlencode

import requests
from flask import Blueprint, current_app, jsonify, redirect, request

from payment.provider.provider_account.application.command.provider_account_command_service import (
    ProviderAccountCommandService
)
from payment.provider.provider_account.application.queries.provider_account_query_service import (
    ProviderAccountQueryService
)
from payment.provider.provider_account.domain.entities.provider_account import (
    EnvKind, ProviderKind, ProviderAccountStatus
)


# ----------------- Helpers -----------------

def _get_services() -> tuple[ProviderAccountCommandService, ProviderAccountQueryService]:
    services = current_app.config.get("services") or {}
    cmd: ProviderAccountCommandService = services["provider_account_command_service"]
    qry: ProviderAccountQueryService = services["provider_account_query_service"]
    return cmd, qry


def _env_kind(env_str: str) -> EnvKind:
    try:
        return EnvKind(env_str)
    except Exception:
        for e in EnvKind:
            if e.value.lower() == str(env_str).lower():
                return e
        raise ValueError(f"env inválido: {env_str}")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _pack_state(party_id: int, env: str) -> str:
    raw = json.dumps({"party_id": party_id, "env": env}, separators=(",", ":")).encode("utf-8")
    return _b64url(raw)


def _unpack_state(state: str) -> dict:
    # agrega padding por si hizo strip
    pad = "=" * ((4 - len(state) % 4) % 4)
    raw = base64.urlsafe_b64decode((state + pad).encode("utf-8"))
    return json.loads(raw.decode("utf-8"))


def _cfg_for_env(env: EnvKind) -> dict:
    if env == EnvKind.TEST:
        return {
            "client_id": current_app.config.get("MP_CLIENT_ID_TEST") or os.getenv("MP_CLIENT_ID_TEST"),
            "client_secret": current_app.config.get("MP_CLIENT_SECRET_TEST") or os.getenv("MP_CLIENT_SECRET_TEST"),
        }
    return {
        "client_id": current_app.config.get("MP_CLIENT_ID_PROD") or os.getenv("MP_CLIENT_ID_PROD"),
        "client_secret": current_app.config.get("MP_CLIENT_SECRET_PROD") or os.getenv("MP_CLIENT_SECRET_PROD"),
    }


# ----------------- Blueprint -----------------

def create_mp_oauth_blueprint() -> Blueprint:
    """
    OAuth (Authorization Code) con client_secret (sin PKCE):
      GET  /connect?party_id=<int>&env=test|prod  -> redirige a MP
      GET  /callback?code=...&state=...          -> token exchange (client_id + client_secret) + upsert provider_account
      POST /refresh/<account_id>                 -> refresh_token (client_secret)
    """
    bp = Blueprint("mp_oauth", __name__)

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True), 200

    @bp.route("/connect", methods=["GET"])
    def connect():
        # inputs
        try:
            party_id = int(request.args.get("party_id", ""))
            env_str = request.args.get("env", "test")
        except Exception:
            return jsonify(ok=False, error="party_id (int) y env (test|prod) son requeridos"), 400

        env = _env_kind(env_str)
        cfg = _cfg_for_env(env)

        client_id = cfg["client_id"]
        client_secret = cfg["client_secret"]
        redirect_uri = current_app.config.get("MP_REDIRECT_URI") or os.getenv("MP_REDIRECT_URI")

        if not client_id or not client_secret or not redirect_uri:
            return jsonify(ok=False, error="Config incompleta: MP_CLIENT_ID_*, MP_CLIENT_SECRET_*, MP_REDIRECT_URI"), 500

        state = _pack_state(party_id, env.value)

        # URL base de autorización
        auth_base = current_app.config.get("MP_AUTH_BASE_URL") or os.getenv("MP_AUTH_BASE_URL") or \
                    "https://auth.mercadopago.com/authorization"

        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "state": state,
        }
        url = f"{auth_base}?{urlencode(params)}"
        return redirect(url, code=302)

    @bp.route("/callback", methods=["GET"])
    def callback():
        code = request.args.get("code")
        state = request.args.get("state")
        if not code or not state:
            return jsonify(ok=False, error="Faltan parámetros code/state"), 400

        # decode state
        try:
            data = _unpack_state(state)
            party_id = int(data["party_id"])
            env = _env_kind(data["env"])
        except Exception:
            return jsonify(ok=False, error="state inválido"), 400

        cfg = _cfg_for_env(env)
        client_id = cfg["client_id"]
        client_secret = cfg["client_secret"]
        redirect_uri = current_app.config.get("MP_REDIRECT_URI") or os.getenv("MP_REDIRECT_URI")

        token_url = current_app.config.get("MP_TOKEN_URL") or os.getenv("MP_TOKEN_URL") or \
                    "https://api.mercadopago.com/oauth/token"
        api_base = current_app.config.get("MP_API_BASE_URL") or os.getenv("MP_API_BASE_URL") or \
                   "https://api.mercadopago.com"

        if not client_id or not client_secret or not redirect_uri:
            return jsonify(ok=False, error="Config OAuth incompleta"), 500

        # ----- 1) Intercambio de code -> tokens (client_secret)
        payload = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        r = requests.post(token_url, data=payload, timeout=30)
        if r.status_code >= 400:
            return jsonify(ok=False, error="token_exchange_failed", details=r.text), 400
        tok = r.json()

        access_token = tok.get("access_token")
        refresh_token = tok.get("refresh_token")
        expires_in = tok.get("expires_in")  # segundos
        expires_at = int(time.time()) + int(expires_in or 0) if expires_in else None

        if not access_token:
            return jsonify(ok=False, error="sin_access_token", details=tok), 400

        # ----- 2) Identificar vendedor (collector_id)
        r2 = requests.get(f"{api_base}/users/me", headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
        if r2.status_code >= 400:
            return jsonify(ok=False, error="users_me_failed", details=r2.text), 400
        me = r2.json()
        collector_id = str(me.get("id") or me.get("user_id") or "")
        if not collector_id:
            return jsonify(ok=False, error="collector_id_not_found"), 400

        public_key = current_app.config.get("MP_PUBLIC_KEY_TEST") or os.getenv("MP_PUBLIC_KEY_TEST")

        # ----- 3) Guardar / upsert en provider_accounts
        cmd, qry = _get_services()
        provider = ProviderKind.MERCADOPAGO

        secret_json_enc = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "client_id": client_id,
            "client_secret": client_secret,
            "collector_id": collector_id,
        }

        entity = cmd.upsert(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_account_id=collector_id,
            public_key=public_key,
            secret_json_enc=secret_json_enc,   # en prod: cifrar
            status=ProviderAccountStatus.ACTIVE,
        )

        return jsonify(ok=True, provider_account_id=entity.id, collector_id=collector_id), 200

    @bp.route("/refresh/<int:account_id>", methods=["POST"])
    def refresh(account_id: int):
        cmd, qry = _get_services()
        entity = qry.get_by_id(account_id)
        if not entity:
            return jsonify(ok=False, error="account_not_found"), 404

        env = entity.env if hasattr(entity.env, "value") else EnvKind(str(entity.env))
        cfg = _cfg_for_env(env)
        client_id = cfg["client_id"]
        client_secret = cfg["client_secret"]
        token_url = current_app.config.get("MP_TOKEN_URL") or os.getenv("MP_TOKEN_URL") or \
                    "https://api.mercadopago.com/oauth/token"

        secrets_dict = entity.secret_json_enc or {}
        refresh_token = secrets_dict.get("refresh_token")
        if not refresh_token:
            return jsonify(ok=False, error="no_refresh_token"), 400

        payload = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }
        r = requests.post(token_url, data=payload, timeout=30)
        if r.status_code >= 400:
            return jsonify(ok=False, error="refresh_failed", details=r.text), 400
        tok = r.json()

        secrets_dict.update({
            "access_token": tok.get("access_token"),
            "refresh_token": tok.get("refresh_token") or refresh_token,
            "expires_at": int(time.time()) + int(tok.get("expires_in") or 0),
        })
        cmd.rotate_secrets(account_id, secrets_dict)
        return jsonify(ok=True), 200

    return bp
