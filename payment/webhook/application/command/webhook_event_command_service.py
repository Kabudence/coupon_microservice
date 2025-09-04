from __future__ import annotations

from typing import Optional, Any, Dict

from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum
from payment.webhook.domain.entities.webhook_event import WebhookEventData
from payment.webhook.infraestructure.repositories.webhook_event_repository import WebhookEventRepository


class WebhookEventCommandService:
    """
    Orquestador de escritura para Webhook Events.
    Separa controller/HTTP de persistencia e idempotencia.
    """
    def __init__(self, repo: WebhookEventRepository):
        self.repo = repo

    def record_incoming(
        self,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        delivery_key: str,
        *,
        topic: Optional[str] = None,
        action: Optional[str] = None,
        resource_id: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        signature_valid: Optional[bool] = None,
        http_status_sent: Optional[int] = None,
        idempotent: bool = True
    ) -> WebhookEventData:
        """
        Inserta el webhook (o retorna existente si idempotente).
        Úsalo en tu endpoint HTTP justo después de parsear headers/body.
        """
        if idempotent:
            return self.repo.ensure_received(
                provider=provider,
                env=env,
                delivery_key=delivery_key,
                topic=topic,
                action=action,
                resource_id=resource_id,
                headers=headers,
                body=body,
                signature_valid=signature_valid,
                http_status_sent=http_status_sent,
            )
        return self.repo.create(
            provider=provider,
            env=env,
            delivery_key=delivery_key,
            topic=topic,
            action=action,
            resource_id=resource_id,
            headers=headers,
            body=body,
            signature_valid=signature_valid,
            http_status_sent=http_status_sent,
        )

    def set_http_status(self, id_: int, status_code: int) -> Optional[WebhookEventData]:
        return self.repo.set_http_status(id_, status_code)

    def set_signature_valid(self, id_: int, is_valid: bool) -> Optional[WebhookEventData]:
        return self.repo.set_signature_valid(id_, is_valid)

    def mark_processed(self, id_: int) -> Optional[WebhookEventData]:
        """
        Llama esto cuando tu worker ya procesó (actualizó órdenes, etc.).
        """
        return self.repo.mark_processed(id_)

    def update_payload_by_delivery_key(
        self,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        delivery_key: str,
        **kwargs
    ) -> Optional[WebhookEventData]:
        return self.repo.update_payload_by_delivery_key(provider, env, delivery_key, **kwargs)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
