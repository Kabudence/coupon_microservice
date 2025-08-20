from __future__ import annotations
from typing import Optional, List

from coupons.category.domain.entities.category import CategoryData
from coupons.category.infraestructure.model.category_model import CategoryModel


class CategoryRepository:
    def _to_entity(self, rec: CategoryModel) -> CategoryData:
        return CategoryData(
            id=rec.id,
            nombre=rec.nombre,
            description=rec.description,
            created_at=rec.created_at,
        )

    def get_by_id(self, id_: int) -> Optional[CategoryData]:
        try:
            rec = CategoryModel.get(CategoryModel.id == id_)
            return self._to_entity(rec)
        except CategoryModel.DoesNotExist:
            return None

    def get_by_nombre(self, nombre: str) -> Optional[CategoryData]:
        if not nombre:
            return None
        try:
            rec = CategoryModel.get(CategoryModel.nombre == nombre.strip())
            return self._to_entity(rec)
        except CategoryModel.DoesNotExist:
            return None

    def list_all(self) -> List[CategoryData]:
        return [self._to_entity(r) for r in CategoryModel.select().order_by(CategoryModel.nombre.asc())]

    def create(self, cat: CategoryData) -> CategoryData:
        rec = CategoryModel.create(
            nombre=cat.nombre,
            description=cat.description,
        )
        return self._to_entity(rec)

    def update(self, cat: CategoryData) -> Optional[CategoryData]:
        try:
            rec = CategoryModel.get(CategoryModel.id == cat.id)
            rec.nombre = cat.nombre
            rec.description = cat.description
            rec.save()
            return self._to_entity(rec)
        except CategoryModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = CategoryModel.get(CategoryModel.id == id_)
            rec.delete_instance()
            return True
        except CategoryModel.DoesNotExist:
            return False
