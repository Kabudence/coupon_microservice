from __future__ import annotations

from typing import Optional, List

from peewee import IntegrityError

from payment.provider.provider_customer.domain.entities.provider_customer import ProviderCustomerData
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum, ProviderCustomerStatus
from payment.provider.provider_customer.infraestructure.model.provider_customer_model import ProviderCustomerModel


class ProviderCustomerRepository:
    # -----------------------
    # Mappers
    # -----------------------
    def _to_entity(self, rec: ProviderCustomerModel) -> ProviderCustomerData:
        return ProviderCustomerData(
            id=rec.id,
            party_id=rec.party_id,
            provider=ProviderEnum(rec.provider),
            env=EnvEnum(rec.env),
            provider_customer_id=rec.provider_customer_id,
            status=ProviderCustomerStatus(rec.status),
            created_at=rec.created_at,
            updated_at=rec.updated_at,
        )

    # -----------------------
    # Queries
    # -----------------------
    def get_by_id(self, id_: int) -> Optional[ProviderCustomerData]:
        try:
            rec = ProviderCustomerModel.get(ProviderCustomerModel.id == id_)
            return self._to_entity(rec)
        except ProviderCustomerModel.DoesNotExist:
            return None

    def get_by_party_provider_env(
        self, party_id: int, provider: ProviderEnum | str, env: EnvEnum | str
    ) -> Optional[ProviderCustomerData]:
        provider = ProviderEnum(str(provider)).value
        env = EnvEnum(str(env)).value
        try:
            rec = (ProviderCustomerModel
                   .select()
                   .where(
                       (ProviderCustomerModel.party_id == party_id) &
                       (ProviderCustomerModel.provider == provider) &
                       (ProviderCustomerModel.env == env)
                   )).get()
            return self._to_entity(rec)
        except ProviderCustomerModel.DoesNotExist:
            return None

    def get_by_provider_external_id(
        self, provider: ProviderEnum | str, env: EnvEnum | str, provider_customer_id: str
    ) -> Optional[ProviderCustomerData]:
        provider = ProviderEnum(str(provider)).value
        env = EnvEnum(str(env)).value
        try:
            rec = (ProviderCustomerModel
                   .select()
                   .where(
                       (ProviderCustomerModel.provider == provider) &
                       (ProviderCustomerModel.env == env) &
                       (ProviderCustomerModel.provider_customer_id == provider_customer_id)
                   )).get()
            return self._to_entity(rec)
        except ProviderCustomerModel.DoesNotExist:
            return None

    def list_by_party(self, party_id: int) -> List[ProviderCustomerData]:
        q = ProviderCustomerModel.select().where(ProviderCustomerModel.party_id == party_id)
        return [self._to_entity(r) for r in q]

    def list_all(self, limit: int = 100, offset: int = 0) -> List[ProviderCustomerData]:
        q = (ProviderCustomerModel
             .select()
             .order_by(ProviderCustomerModel.id.desc())
             .limit(limit)
             .offset(offset))
        return [self._to_entity(r) for r in q]

    # -----------------------
    # Commands
    # -----------------------
    def create(self, entity: ProviderCustomerData) -> ProviderCustomerData:
        try:
            rec = ProviderCustomerModel.create(
                party_id=entity.party_id,
                provider=entity.provider.value if hasattr(entity.provider, "value") else str(entity.provider),
                env=entity.env.value if hasattr(entity.env, "value") else str(entity.env),
                provider_customer_id=entity.provider_customer_id,
                status=entity.status.value if hasattr(entity.status, "value") else str(entity.status),
            )
            return self._to_entity(rec)
        except IntegrityError as e:
            # Únicos posibles a violar: (party,provider,env) o (provider,env,provider_customer_id)
            raise ValueError(f"provider_customer duplicado (índices únicos): {e}")

    def update(self, entity: ProviderCustomerData) -> Optional[ProviderCustomerData]:
        try:
            rec = ProviderCustomerModel.get(ProviderCustomerModel.id == entity.id)
            rec.party_id = entity.party_id
            rec.provider = entity.provider.value if hasattr(entity.provider, "value") else str(entity.provider)
            rec.env = entity.env.value if hasattr(entity.env, "value") else str(entity.env)
            rec.provider_customer_id = entity.provider_customer_id
            rec.status = entity.status.value if hasattr(entity.status, "value") else str(entity.status)
            rec.save()
            return self._to_entity(rec)
        except ProviderCustomerModel.DoesNotExist:
            return None
        except IntegrityError as e:
            raise ValueError(f"conflicto de unicidad al actualizar provider_customer: {e}")

    def upsert_by_party(
        self,
        party_id: int,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        provider_customer_id: str,
        status: ProviderCustomerStatus | str = ProviderCustomerStatus.ACTIVE,
    ) -> ProviderCustomerData:
        """
        Idempotente por (party_id, provider, env).
        - Si existe: actualiza provider_customer_id y status si cambiaron.
        - Si no: crea la fila.
        """
        existing = self.get_by_party_provider_env(party_id, provider, env)
        if existing:
            changed = False
            if existing.provider_customer_id != provider_customer_id:
                existing.provider_customer_id = provider_customer_id
                changed = True
            if str(existing.status.value if hasattr(existing.status, "value") else existing.status) != \
               str(status.value if hasattr(status, "value") else status):
                existing.status = status
                changed = True
            return self.update(existing) if changed else existing

        # crear
        entity = ProviderCustomerData(
            party_id=party_id,
            provider=provider,
            env=env,
            provider_customer_id=provider_customer_id,
            status=status,
        )
        return self.create(entity)

    def set_status(
        self,
        party_id: int,
        provider: ProviderEnum | str,
        env: EnvEnum | str,
        status: ProviderCustomerStatus | str
    ) -> Optional[ProviderCustomerData]:
        existing = self.get_by_party_provider_env(party_id, provider, env)
        if not existing:
            return None
        existing.status = status
        return self.update(existing)

    def delete(self, id_: int) -> bool:
        try:
            rec = ProviderCustomerModel.get(ProviderCustomerModel.id == id_)
            rec.delete_instance()
            return True
        except ProviderCustomerModel.DoesNotExist:
            return False
