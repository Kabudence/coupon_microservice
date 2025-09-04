from __future__ import annotations

import hashlib
import hmac
from typing import Any, Dict, Optional, Tuple

from flask import Blueprint, request, jsonify, current_app

from payment.provider.provider_customer.domain.value_objects.enums import (
    ProviderEnum, EnvEnum
)
from payment.webhook.application.command.webhook_event_command_service import WebhookEventCommandService
from payment.webhook.application.queries.webhook_event_query_service import WebhookEventQueryService


# -------- Helpers --------

def _raw_body() -> bytes:
    # IMPORTANTE: cache=True para que luego request.get_json() pueda leer el mismo cuerpo.
    return request.get_data(cache=True, as_text=False) or b""


def _env_from_payload(payload: Dict[str, Any]) -> EnvEnum:
    # Permite override por query ?env=test|prod (útil en pruebas)
    qs_env = (request.args.get("env") or "").strip().lower()
    if qs_env in ("test", "prod"):
        return EnvEnum.TEST if qs_env == "test" else EnvEnum.PROD

    # Mercado Pago: live_mode True = prod, False = test
    live = bool(payload.get("live_mode", False))
    return EnvEnum.PROD if live else EnvEnum.TEST


def _topic_action_resource(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    topic = payload.get("type") or payload.get("topic")
    action = payload.get("action")

    resource_id = None
    data = payload.get("data") or {}
    if isinstance(data, dict):
        resource_id = data.get("id") or data.get("resource_id")

    if not resource_id and isinstance(payload.get("resource"), dict):
        resource_id = payload["resource"].get("id")

    if not resource_id and payload.get("id"):
        resource_id = payload["id"]

    return topic, action, (str(resource_id) if resource_id is not None else None)


def _delivery_key(headers: Dict[str, str], raw: bytes) -> str:
    candidates = [
        "X-Request-Id",
        "X-Mercadopago-Delivery-Id",
        "X-Delivery-Id",
        "X-Idempotency-Key",
    ]
    for h in candidates:
        v = headers.get(h) or headers.get(h.lower())
        if v:
            return v
    import hashlib as _hash
    return _hash.sha256(raw or b"").hexdigest()


def _verify_hmac_if_configured(headers: Dict[str, str], raw: bytes) -> Optional[bool]:
    """
    Verifica firma HMAC si configuras MP_WEBHOOK_SECRET en app.config.
    Espera header 'X-Signature' con formato 'sha256=<hex>'.
    Si no hay secreto, devuelve None (no se verifica).
    """
    secret = current_app.config.get("MP_WEBHOOK_SECRET")
    if not secret:
        return None

    hdr = headers.get("X-Signature") or headers.get("x-signature")
    if not hdr or "=" not in hdr:
        return False
    algo, provided = hdr.split("=", 1)
    if algo.lower() != "sha256":
        return False

    mac = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, provided.strip())


# -------- Blueprint Factory (usa container) --------

def create_mp_webhook_blueprint(url_prefix: str = "/webhooks/mp") -> Blueprint:
    """
    Crea un blueprint que responde webhooks de Mercado Pago.
    Usa services desde current_app.config["services"] construido por tu container.
    """
    bp = Blueprint("mp_webhooks", __name__)
    provider = ProviderEnum.MERCADOPAGO

    def _get_services() -> tuple[WebhookEventCommandService, WebhookEventQueryService]:
        services = current_app.config.get("services") or {}
        cmd: WebhookEventCommandService = services["webhook_command_service"]
        qry: WebhookEventQueryService = services["webhook_query_service"]
        return cmd, qry

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True, provider=provider.value), 200

    @bp.route("", methods=["POST"])
    def receive():
        cmd, _qry = _get_services()

        # Congelamos el body UNA sola vez, disponible para todo lo demás.
        raw = _raw_body()
        headers = {k: v for k, v in request.headers.items()}

        # No volvemos a llamar a request.get_data(); si quieres log, usa 'raw'.
        # print("RAW:", raw.decode("utf-8", errors="ignore"))

        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(ok=False, error="invalid_json"), 400

        env = _env_from_payload(payload)
        topic, action, resource_id = _topic_action_resource(payload)
        delivery_key = _delivery_key(headers, raw)
        sig_valid = _verify_hmac_if_configured(headers, raw)

        event = cmd.record_incoming(
            provider=provider,
            env=env,
            delivery_key=delivery_key,
            topic=topic,
            action=action,
            resource_id=resource_id,
            headers=headers,
            body=payload,
            signature_valid=sig_valid,
            http_status_sent=None,
            idempotent=True,
        )

        # Aquí podrías encolar un job async para consultar el pago y actualizar tu orden.

        cmd.set_http_status(event.id, 200)
        return jsonify(ok=True, event_id=event.id), 200

    bp.url_prefix = url_prefix
    return bp
