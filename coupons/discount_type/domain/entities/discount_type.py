from enum import Enum


class DiscountTypeName(Enum):
    PERCENTAGE = "PORCENTAJE"
    AMOUNT = "MONTO"


class DiscountTypeData:
    def __init__(self, id: int = None, name: str = ""):
        self.id = id
        if name is None or str(name).strip() == "":
            raise ValueError("name cannot be None or empty")

        # Accepts Enum or string, normalize to string
        if isinstance(name, DiscountTypeName):
            self.name = name.value
        else:
            self.name = str(name).strip()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }