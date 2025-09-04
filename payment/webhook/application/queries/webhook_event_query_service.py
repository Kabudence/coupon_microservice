from __future__ import annotations

from typing import Optional, List

from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum
from payment.webhook.domain.entities.webhook_event import WebhookEventData
from payment.webhook.infraestructure.repositories.webhook_event_repository import WebhookEventRepository


class WebhookEventQueryService:
    """
    Casos de uso de lectura para Webhook Events.
    """
    def __init__(self, repo: WebhookEventRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[WebhookEventData]:
        return self.repo.get_by_id(id_)

    def get_by_delivery_key(self, provider: ProviderEnum | str, env: EnvEnum | str, delivery_key: str) -> Optional[WebhookEventData]:
        return self.repo.get_by_delivery_key(provider, env, delivery_key)

    def find_by_resource(self, provider: ProviderEnum | str, env: EnvEnum | str, resource_id: str,
                         limit: int = 100, offset: int = 0) -> List[WebhookEventData]:
        return self.repo.find_by_resource(provider, env, resource_id, limit=limit, offset=offset)

    def list_unprocessed(self, provider: ProviderEnum | str | None = None,
                         env: EnvEnum | str | None = None,
                         limit: int = 100, offset: int = 0) -> List[WebhookEventData]:
        return self.repo.list_unprocessed(provider=provider, env=env, limit=limit, offset=offset)

    def list_recent(self, limit: int = 100, offset: int = 0) -> List[WebhookEventData]:
        return self.repo.list_recent(limit=limit, offset=offset)
