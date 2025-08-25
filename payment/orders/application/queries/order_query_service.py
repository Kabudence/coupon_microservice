from payment.orders.domain.entities.order import OrderData
from payment.orders.domain.value_objects.enums import OrderStatus, PaymentFlow
from payment.orders.infraestructure.repositories.order_repository import OrderRepository
from payment.provider.provider_customer.domain.value_objects.enums import ProviderEnum, EnvEnum
from typing import Optional, List

class OrderQueryService:
    """
    Casos de uso de lectura para Orders.
    """
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[OrderData]:
        return self.repo.get_by_id(id_)

    def get_by_provider_payment(self, provider: ProviderEnum | str, env: EnvEnum | str, provider_payment_id: str) -> Optional[OrderData]:
        return self.repo.get_by_provider_payment(provider, env, provider_payment_id)

    def get_by_idempotency(self, provider: ProviderEnum | str, env: EnvEnum | str, idempotency_key: str) -> Optional[OrderData]:
        return self.repo.get_by_idempotency(provider, env, idempotency_key)

    def list_by_buyer(self, buyer_party_id: int, status: Optional[OrderStatus | str] = None, limit: int = 100, offset: int = 0) -> List[OrderData]:
        return self.repo.list_by_buyer(buyer_party_id, status=status, limit=limit, offset=offset)

    def list_by_seller(self, seller_party_id: int, status: Optional[OrderStatus | str] = None, limit: int = 100, offset: int = 0) -> List[OrderData]:
        return self.repo.list_by_seller(seller_party_id, status=status, limit=limit, offset=offset)

    def list_by_status(self, status: OrderStatus | str, limit: int = 100, offset: int = 0) -> List[OrderData]:
        return self.repo.list_by_status(status, limit=limit, offset=offset)