from typing import Optional, List

from coupons.discount_type.domain.entities.discount_type import DiscountTypeData, DiscountTypeName
from coupons.discount_type.infraestructure.model.discount_type_model import DiscountTypeModel


class DiscountTypeRepository:
    def get_by_id(self, id_: int) -> Optional[DiscountTypeData]:
        try:
            rec = DiscountTypeModel.get(DiscountTypeModel.id == id_)
            return DiscountTypeData(id=rec.id, name=rec.name)
        except DiscountTypeModel.DoesNotExist:
            return None

    def get_all(self) -> List[DiscountTypeData]:
        return [
            DiscountTypeData(id=rec.id, name=rec.name)
            for rec in DiscountTypeModel.select()
        ]

    def find_by_name(self, name: Optional[str]) -> List[DiscountTypeData]:
        if not name:
            return []
        q = DiscountTypeModel.select().where(
            DiscountTypeModel.name == (
                name.value if isinstance(name, DiscountTypeName) else name
            )
        )
        return [DiscountTypeData(id=rec.id, name=rec.name) for rec in q]

    def create(self, discount_type: DiscountTypeData) -> DiscountTypeData:
        rec = DiscountTypeModel.create(
            name=discount_type.name if not isinstance(discount_type.name, DiscountTypeName)
                 else discount_type.name.value
        )
        return DiscountTypeData(id=rec.id, name=rec.name)

    def update(self, discount_type: DiscountTypeData) -> Optional[DiscountTypeData]:
        try:
            rec = DiscountTypeModel.get(DiscountTypeModel.id == discount_type.id)
            rec.name = (discount_type.name.value
                        if isinstance(discount_type.name, DiscountTypeName)
                        else discount_type.name)
            rec.save()
            return DiscountTypeData(id=rec.id, name=rec.name)
        except DiscountTypeModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = DiscountTypeModel.get(DiscountTypeModel.id == id_)
            rec.delete_instance()
            return True
        except DiscountTypeModel.DoesNotExist:
            return False
