from payment.provider.customer_sources.domain.entities.payment_source import PaymentSourceData
from payment.provider.customer_sources.infraestructure.repositories.payment_source_repository import PaymentSourceRepository
from typing import Optional, List
class PaymentSourceQueryService:
    """
    Casos de uso de LECTURA para payment_sources.
    """
    def __init__(self, repo: PaymentSourceRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[PaymentSourceData]:
        return self.repo.get_by_id(id_)

    def get_by_customer_and_source_id(self, provider_customer_pk: int, provider_source_id: str) -> Optional[PaymentSourceData]:
        return self.repo.get_by_customer_and_source_id(provider_customer_pk, provider_source_id)

    def list_by_customer(self, provider_customer_pk: int, only_active: bool = True) -> List[PaymentSourceData]:
        return self.repo.list_by_customer(provider_customer_pk, only_active=only_active)

    def list_active_cards(self, provider_customer_pk: int) -> List[PaymentSourceData]:
        return self.repo.list_active_cards(provider_customer_pk)

    def get_wallet(self, provider_customer_pk: int) -> Optional[PaymentSourceData]:
        return self.repo.get_wallet(provider_customer_pk)