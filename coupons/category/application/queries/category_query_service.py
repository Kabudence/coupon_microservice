from __future__ import annotations
from typing import Optional, List

from coupons.category.domain.entities.category import CategoryData
from coupons.category.infraestructure.repositories.category_repository import CategoryRepository


class CategoryQueryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[CategoryData]:
        return self.repo.get_by_id(id_)

    def get_by_nombre(self, nombre: str) -> Optional[CategoryData]:
        return self.repo.get_by_nombre(nombre)

    def list_all(self) -> List[CategoryData]:
        return self.repo.list_all()
