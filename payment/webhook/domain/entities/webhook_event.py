from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Dict

from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum


@dataclass
class WebhookEventData:
    """
    Representa un evento de webhook recibido desde un proveedor (MP/Stripe/etc.).

    NOTAS:
    - 'delivery_key' es tu llave de idempotencia de recepción (p.ej. X-Request-Id, id de evento,
      o una combinación que garantice unicidad). En DB es UNIQUE por (provider, env, delivery_key).
    - 'headers' y 'body' se guardan como JSON (dict serializable).
    - 'signature_valid' la marca tu verificador de firma si aplica (0/1).
    - 'http_status_sent' es el status que tu endpoint devolvió al proveedor.
    - 'processed_at' se setea cuando tu app ya procesó el evento.
    """
    id: Optional[int] = None

    provider: ProviderEnum | str = ProviderEnum.MERCADOPAGO
    env: EnvEnum | str = EnvEnum.TEST
    topic: Optional[str] = None
    action: Optional[str] = None
    resource_id: Optional[str] = None
    delivery_key: Optional[str] = None

    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None

    signature_valid: Optional[bool] = None
    http_status_sent: Optional[int] = None

    received_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    def __post_init__(self):
        # Normalizar enums
        if not isinstance(self.provider, ProviderEnum):
            self.provider = ProviderEnum(str(self.provider))
        if not isinstance(self.env, EnvEnum):
            self.env = EnvEnum(str(self.env))

        # Validaciones mínimas
        if not self.delivery_key or not str(self.delivery_key).strip():
            raise ValueError("delivery_key es requerido para idempotencia")
        # provider/env ya están normalizados arriba

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "provider": self.provider.value if isinstance(self.provider, ProviderEnum) else str(self.provider),
            "env": self.env.value if isinstance(self.env, EnvEnum) else str(self.env),
            "topic": self.topic,
            "action": self.action,
            "resource_id": self.resource_id,
            "delivery_key": self.delivery_key,
            "headers": self.headers,
            "body": self.body,
            "signature_valid": bool(self.signature_valid) if self.signature_valid is not None else None,
            "http_status_sent": self.http_status_sent,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
