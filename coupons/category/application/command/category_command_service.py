from __future__ import annotations
from typing import Optional

from coupons.category.domain.entities.category import CategoryData
from coupons.category.infraestructure.repositories.category_repository import CategoryRepository


class CategoryCommandService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def create(self, nombre: str, description: Optional[str] = None) -> CategoryData:
        entity = CategoryData(nombre=nombre, description=description)
        # Unicidad por nombre
        existing = self.repo.get_by_nombre(entity.nombre)
        if existing:
            raise ValueError(f"Category with nombre '{entity.nombre}' already exists.")
        return self.repo.create(entity)

    def update(self, id_: int, nombre: str, description: Optional[str] = None) -> CategoryData:
        current = self.repo.get_by_id(id_)
        if not current:
            raise ValueError("Category not found.")

        # Si cambia el nombre, validar unicidad
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("nombre cannot be empty.")
        other = self.repo.get_by_nombre(nombre)
        if other and other.id != id_:
            raise ValueError(f"Category with nombre '{nombre}' already exists.")

        current.nombre = nombre
        current.description = (description.strip() if isinstance(description, str) else description)

        updated = self.repo.update(current)
        if not updated:
            raise ValueError("Category not found.")
        return updated

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
