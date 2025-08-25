from __future__ import annotations

import datetime
from typing import Optional, List

from peewee import IntegrityError

from payment.checkout.domain.entities.checkout_session import CheckoutSessionData
from payment.checkout.infraestructure.model.checkout_session_model import CheckoutSessionModel


class CheckoutSessionRepository:
    # -----------------------
    # Mappers
    # -----------------------
    def _to_entity(self, rec: CheckoutSessionModel) -> CheckoutSessionData:
        return CheckoutSessionData(
            id=rec.id,
            order_id=rec.order_id,
            provider_session_id=rec.provider_session_id,
            init_url=rec.init_url,
            sandbox_url=rec.sandbox_url,
            expires_at=rec.expires_at,
            created_at=rec.created_at,
        )

    # -----------------------
    # Queries
    # -----------------------
    def get_by_id(self, id_: int) -> Optional[CheckoutSessionData]:
        try:
            rec = CheckoutSessionModel.get(CheckoutSessionModel.id == id_)
            return self._to_entity(rec)
        except CheckoutSessionModel.DoesNotExist:
            return None

    def get_by_provider_session_id(self, provider_session_id: str) -> Optional[CheckoutSessionData]:
        try:
            rec = (CheckoutSessionModel
                   .select()
                   .where(CheckoutSessionModel.provider_session_id == provider_session_id)
                   ).get()
            return self._to_entity(rec)
        except CheckoutSessionModel.DoesNotExist:
            return None

    def list_by_order(self, order_id: int, only_active: bool = False) -> List[CheckoutSessionData]:
        q = CheckoutSessionModel.select().where(CheckoutSessionModel.order_id == order_id)
        if only_active:
            now = datetime.datetime.now()
            q = q.where((CheckoutSessionModel.expires_at.is_null(True)) | (CheckoutSessionModel.expires_at > now))
        q = q.order_by(CheckoutSessionModel.id.desc())
        return [self._to_entity(r) for r in q]

    # -----------------------
    # Commands
    # -----------------------
    def create(self, entity: CheckoutSessionData) -> CheckoutSessionData:
        try:
            rec = CheckoutSessionModel.create(
                order_id=entity.order_id,
                provider_session_id=entity.provider_session_id,
                init_url=entity.init_url,
                sandbox_url=entity.sandbox_url,
                expires_at=entity.expires_at,
            )
            return self._to_entity(rec)
        except IntegrityError as e:
            # Único posible: provider_session_id
            raise ValueError(f"checkout_session duplicado (provider_session_id): {e}")

    def update(self, entity: CheckoutSessionData) -> Optional[CheckoutSessionData]:
        try:
            rec = CheckoutSessionModel.get(CheckoutSessionModel.id == entity.id)
            rec.order_id = entity.order_id
            rec.provider_session_id = entity.provider_session_id
            rec.init_url = entity.init_url
            rec.sandbox_url = entity.sandbox_url
            rec.expires_at = entity.expires_at
            rec.save()
            return self._to_entity(rec)
        except CheckoutSessionModel.DoesNotExist:
            return None
        except IntegrityError as e:
            raise ValueError(f"conflicto de unicidad al actualizar checkout_session: {e}")

    def delete(self, id_: int) -> bool:
        try:
            rec = CheckoutSessionModel.get(CheckoutSessionModel.id == id_)
            rec.delete_instance()
            return True
        except CheckoutSessionModel.DoesNotExist:
            return False

    # -----------------------
    # Helpers de uso común
    # -----------------------
    def expire_all_for_order(self, order_id: int) -> int:
        """Marca todas las sesiones de una orden como expiradas desde 'now'."""
        now = datetime.datetime.now()
        q = (CheckoutSessionModel
             .update({CheckoutSessionModel.expires_at: now})
             .where(CheckoutSessionModel.order_id == order_id))
        return q.execute()

    def create_or_replace_for_order(
        self,
        order_id: int,
        provider_session_id: str,
        init_url: str | None,
        sandbox_url: str | None,
        expires_at: datetime.datetime | None = None,
        expire_previous: bool = True
    ) -> CheckoutSessionData:
        """
        Crea una nueva sesión para la orden. Opcionalmente expira las anteriores.
        Útil cuando regeneras una preference de MP.
        """
        if expire_previous:
            self.expire_all_for_order(order_id)

        entity = CheckoutSessionData(
            order_id=order_id,
            provider_session_id=provider_session_id,
            init_url=init_url,
            sandbox_url=sandbox_url,
            expires_at=expires_at,
        )
        return self.create(entity)

    def update_urls_by_provider_session_id(
        self,
        provider_session_id: str,
        init_url: str | None = None,
        sandbox_url: str | None = None,
        expires_at: datetime.datetime | None = None
    ) -> Optional[CheckoutSessionData]:
        """
        Cuando MP devuelve nuevas URLs (por rotación) o cambias expiración.
        """
        rec = self.get_by_provider_session_id(provider_session_id)
        if not rec:
            return None
        changed = False
        if init_url is not None and rec.init_url != init_url:
            rec.init_url = init_url
            changed = True
        if sandbox_url is not None and rec.sandbox_url != sandbox_url:
            rec.sandbox_url = sandbox_url
            changed = True
        if expires_at is not None and rec.expires_at != expires_at:
            rec.expires_at = expires_at
            changed = True
        return self.update(rec) if changed else rec

    def expire_by_provider_session_id(self, provider_session_id: str) -> Optional[CheckoutSessionData]:
        rec = self.get_by_provider_session_id(provider_session_id)
        if not rec:
            return None
        rec.expires_at = datetime.datetime.now()
        return self.update(rec)
