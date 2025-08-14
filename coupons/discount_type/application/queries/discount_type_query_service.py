from typing import List, Optional

from coupons.discount_type.domain.entities.discount_type import DiscountTypeData, DiscountTypeName
from coupons.discount_type.infraestructure.repositories.discount_type_repository import DiscountTypeRepository


class DiscountTypeQueryService:
    def __init__(self, repo: DiscountTypeRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[DiscountTypeData]:
        return self.repo.get_by_id(id_)

    def list_all(self) -> List[DiscountTypeData]:
        return self.repo.get_all()

    def find_by_name(self, name: Optional[str | DiscountTypeName] = None) -> List[DiscountTypeData]:
        return self.repo.find_by_name(name)
