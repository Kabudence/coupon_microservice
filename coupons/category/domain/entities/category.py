from __future__ import annotations
from typing import Optional
from datetime import datetime


class CategoryData:
    def __init__(
        self,
        id: Optional[int] = None,
        nombre: str = "",
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        if nombre is None or str(nombre).strip() == "":
            raise ValueError("nombre cannot be None or empty")

        self.id = id
        self.nombre = str(nombre).strip()
        self.description = (str(description).strip() if description else None)
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
