# payment/webhook/infraestructure/repositories/webhook_event_repository.py
from __future__ import annotations

import datetime
from typing import Optional, List, Any, Dict

from peewee import IntegrityError

from payment.provider.provider_customer.domain.value_objects.enums import EnvEnum, ProviderEnum
from payment.webhook.domain.entities.webhook_event import WebhookEventData
from payment.webhook.infraestructure.model.webhook_event_model import WebhookEventModel


class WebhookEventRepository:
    # -----------------------
    # Helpers de normalización
    # -----------------------
    @staticmethod
    def _prov_value(provider: ProviderEnum | str) -> str:
        if isinstance(provider, ProviderEnum):
            return provider.value
        # tolerante a mayúsc/minúsculas
        try:
            return ProviderEnum(str(provider)).value
        except Exception:
            for e in ProviderEnum:
                if e.value.lower() == str(provider).lower():
                    return e.value
            raise

    @staticmethod
    def _env_value(env: EnvEnum | str) -> str:
        if isinstance(env, EnvEnum):
            return env.value
        try:
            return EnvEnum(str(env)).value
        except Exception:
            for e in EnvEnum:
                if e.value.lower() == str(env).lower():
                    return e.value
            raise

    # -----------------------
    # Mapper
    # -----------------------
    def _to_entity(self, rec: WebhookEventModel) -> WebhookEventData:
        return WebhookEventData(
            id=rec.id,
            provider=ProviderEnum(rec.provider),
            env=EnvEnum(rec.env),
            topic=rec.topic,
            action=rec.action,
            resource_id=rec.resource_id,
            delivery_key=rec.delivery_key,
            headers=WebhookEventModel._loads(rec.headers),
            body=WebhookEventModel._loads(rec.body),
            signature_valid=rec.signature_valid,
            http_status_sent=rec.http_status_sent,
            received_at=rec.received_at,
            processed_at=rec.processed_at,
        )

    # -----------------------
    # Queries
    # -----------------------
    def get_by_id(self, id_: int) -> Optional[WebhookEventData]:
        try:
            rec = WebhookEventModel.get(WebhookEventModel.id == id_)
            return self._to_entity(rec)
        except WebhookEventModel.DoesNotExist:
            return None

    def get_by_delivery_key(
        self, provider: ProviderEnum | str, env: EnvEnum | str, delivery_key: str
    ) -> Optional[WebhookEventData]:
        provider_v = self._prov_value(provider)
        env_v = self._env_value(env)
        try:
            rec = (WebhookEventModel
                   .select()
                   .where(
                       (WebhookEventModel.provider == provider_v) &
                       (WebhookEventModel.env == env_v) &
                       (WebhookEventModel.delivery_key == delivery_key)
                   )).get()
            return self._to_entity(rec)
        except WebhookEventModel.DoesNotExist:
            return None

    def find_by_resource(
        self, provider: ProviderEnum | str, env: EnvEnum | str, resource_id: str,
        limit: int = 100, offset: int = 0
    ) -> List[WebhookEventData]:
        provider_v = self._prov_value(provider)
        env_v = self._env_value(env)
        q = (WebhookEventModel
             .select()
             .where(
                 (WebhookEventModel.provider == provider_v) &
                 (WebhookEventModel.env == env_v) &
                 (WebhookEventModel.resource_id == resource_id)
             )
             .order_by(WebhookEventModel.id.desc())
             .limit(limit)
             .offset(offset))
        return [self._to_entity(r) for r in q]

    def list_unprocessed(
        self, provider: ProviderEnum | str | None = None,
        env: EnvEnum | str | None = None,
        limit: int = 100, offset: int = 0
    ) -> List[WebhookEventData]:
        q = WebhookEventModel.select().where(WebhookEventModel.processed_at.is_null(True))
        if provider is not None:
            q = q.where(WebhookEventModel.provider == self._prov_value(provider))
        if env is not None:
            q = q.where(WebhookEventModel.env == self._env_value(env))
        q = q.order_by(WebhookEventModel.id.asc()).limit(limit).offset(offset)
        return [self._to_entity(r) for r in q]

    def list_recent(self, limit: int = 100, offset: int = 0) -> List[WebhookEventData]:
        q = (WebhookEventModel
             .select()
             .order_by(WebhookEventModel.id.desc())
             .limit(limit)
             .offset(offset))
        return [self._to_entity(r) for r in q]

    # -----------------------
    # Commands
    # -----------------------
    def create(
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
        http_status_sent: Optional[int] = None
    ) -> WebhookEventData:
        try:
            rec = WebhookEventModel.create(
                provider=self._prov_value(provider),
                env=self._env_value(env),
                topic=topic,
                action=action,
                resource_id=resource_id,
                delivery_key=delivery_key,
                headers=WebhookEventModel._dumps(headers),
                body=WebhookEventModel._dumps(body),
                signature_valid=signature_valid,
                http_status_sent=http_status_sent,
            )
            return self._to_entity(rec)
        except IntegrityError as e:
            # Violación de uq (provider, env, delivery_key)
            raise ValueError(f"webhook duplicado para delivery_key='{delivery_key}': {e}")

    def ensure_received(
        self,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        delivery_key: str,
        **kwargs
    ) -> WebhookEventData:
        """
        Idempotente: si ya existe (provider, env, delivery_key) -> devuelve existente,
        si no, lo crea.
        """
        existing = self.get_by_delivery_key(provider, env, delivery_key)
        if existing:
            return existing
        return self.create(provider, env, delivery_key, **kwargs)

    def mark_processed(self, id_: int) -> Optional[WebhookEventData]:
        try:
            rec = WebhookEventModel.get(WebhookEventModel.id == id_)
            rec.processed_at = datetime.datetime.now()
            rec.save()
            return self._to_entity(rec)
        except WebhookEventModel.DoesNotExist:
            return None

    def set_http_status(self, id_: int, status_code: int) -> Optional[WebhookEventData]:
        try:
            rec = WebhookEventModel.get(WebhookEventModel.id == id_)
            rec.http_status_sent = status_code
            rec.save()
            return self._to_entity(rec)
        except WebhookEventModel.DoesNotExist:
            return None

    def set_signature_valid(self, id_: int, is_valid: bool) -> Optional[WebhookEventData]:
        try:
            rec = WebhookEventModel.get(WebhookEventModel.id == id_)
            rec.signature_valid = bool(is_valid)
            rec.save()
            return self._to_entity(rec)
        except WebhookEventModel.DoesNotExist:
            return None

    def update_payload_by_delivery_key(
        self,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        delivery_key: str,
        *,
        headers: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        topic: Optional[str] = None,
        action: Optional[str] = None,
        resource_id: Optional[str] = None,
        signature_valid: Optional[bool] = None,
        http_status_sent: Optional[int] = None
    ) -> Optional[WebhookEventData]:
        """
        Actualiza el **modelo** (no la entidad) localizado por (provider, env, delivery_key).
        """
        provider_v = self._prov_value(provider)
        env_v = self._env_value(env)

        try:
            rec = (WebhookEventModel
                   .select()
                   .where(
                       (WebhookEventModel.provider == provider_v) &
                       (WebhookEventModel.env == env_v) &
                       (WebhookEventModel.delivery_key == delivery_key)
                   )).get()
        except WebhookEventModel.DoesNotExist:
            return None

        changed = False
        if topic is not None and rec.topic != topic:
            rec.topic = topic; changed = True
        if action is not None and rec.action != action:
            rec.action = action; changed = True
        if resource_id is not None and rec.resource_id != resource_id:
            rec.resource_id = resource_id; changed = True
        if headers is not None:
            rec.headers = WebhookEventModel._dumps(headers); changed = True
        if body is not None:
            rec.body = WebhookEventModel._dumps(body); changed = True
        if signature_valid is not None and rec.signature_valid != signature_valid:
            rec.signature_valid = signature_valid; changed = True
        if http_status_sent is not None and rec.http_status_sent != http_status_sent:
            rec.http_status_sent = http_status_sent; changed = True

        if changed:
            rec.save()
        return self._to_entity(rec)

    def delete(self, id_: int) -> bool:
        try:
            rec = WebhookEventModel.get(WebhookEventModel.id == id_)
            rec.delete_instance()
            return True
        except WebhookEventModel.DoesNotExist:
            return False
