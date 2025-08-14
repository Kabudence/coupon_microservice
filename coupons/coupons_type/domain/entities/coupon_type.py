class CouponTypeData:
    def __init__(self, id: int = None, name: str = "", description: str = ""):
        self.id = id

        if name is None or str(name).strip() == "":
            raise ValueError("name cannot be None or empty")
        self.name = str(name).strip()

        self.description = str(description).strip() if description is not None else None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
