from typing import Optional

from coupons.discount_type.domain.entities.discount_type import DiscountTypeName, DiscountTypeData
from coupons.discount_type.infraestructure.repositories.discount_type_repository import DiscountTypeRepository


class DiscountTypeCommandService:
    def __init__(self, repo: DiscountTypeRepository):
        self.repo = repo

    def create(self, name: str | DiscountTypeName) -> DiscountTypeData:
        if name is None or str(name).strip() == "":
            raise ValueError("name is required")
        entity = DiscountTypeData(name=name)
        return self.repo.create(entity)

    def update(self, id_: int, name: str | DiscountTypeName) -> Optional[DiscountTypeData]:
        current = self.repo.get_by_id(id_)
        if not current:
            raise ValueError("DiscountType not found.")
        current.name = (name.value if isinstance(name, DiscountTypeName) else str(name).strip())
        return self.repo.update(current)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
