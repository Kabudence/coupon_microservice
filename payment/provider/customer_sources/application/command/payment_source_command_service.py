from __future__ import annotations

from typing import Optional

from payment.provider.customer_sources.domain.entities.payment_source import PaymentSourceData
from payment.provider.customer_sources.domain.valueobjects.enums import PaymentSourceStatus
from payment.provider.customer_sources.infraestructure.repositories.payment_source_repository import PaymentSourceRepository
from payment.provider.provider_customer.domain.value_objects.enums import EnvEnum





class PaymentSourceCommandService:
    """
    Casos de uso de ESCRITURA para payment_sources.
    """
    def __init__(self, repo: PaymentSourceRepository):
        self.repo = repo

    def create(self, entity: PaymentSourceData) -> PaymentSourceData:
        return self.repo.create(entity)

    def update(self, entity: PaymentSourceData) -> Optional[PaymentSourceData]:
        return self.repo.update(entity)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)

    def soft_delete(self, id_: int) -> bool:
        return self.repo.soft_delete(id_)

    # Upserts directos
    def upsert_card(
        self,
        provider_customer_pk: int,
        provider_source_id: str,
        brand: str,
        last_four: str,
        exp_month: int,
        exp_year: int,
        holder_name: Optional[str] = None,
        status: PaymentSourceStatus | str = PaymentSourceStatus.ACTIVE,
    ) -> PaymentSourceData:
        return self.repo.upsert_card(
            provider_customer_pk=provider_customer_pk,
            provider_source_id=provider_source_id,
            brand=brand,
            last_four=last_four,
            exp_month=exp_month,
            exp_year=exp_year,
            holder_name=holder_name,
            status=status,
        )

    def upsert_wallet(
        self,
        provider_customer_pk: int,
        holder_name: Optional[str] = None,
        status: PaymentSourceStatus | str = PaymentSourceStatus.ACTIVE,
    ) -> PaymentSourceData:
        return self.repo.upsert_wallet(
            provider_customer_pk=provider_customer_pk,
            holder_name=holder_name,
            status=status,
        )

    # Mercado Pago helpers
    def upsert_from_mp_card_json(
        self,
        provider_customer_pk: int,
        env: EnvEnum | str,
        mp_card: dict,
    ) -> PaymentSourceData:
        return self.repo.upsert_from_mp_card_json(
            provider_customer_pk=provider_customer_pk,
            env=env,
            mp_card=mp_card,
        )
