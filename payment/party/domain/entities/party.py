from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import Optional


class PartyAppName(Enum):
    EMPRENDE = "emprende"
    FULLVENTAS = "fullventas"


class PartySubjectType(Enum):
    USER = "user"
    CLIENT = "client"


class PartyData:
    """
    Party = puente neutro hacia tus propias tablas (user/client).
    Unicidad por (app_name, subject_type, subject_id).
    """
    def __init__(
        self,
        id: Optional[int] = None,
        app_name: PartyAppName | str = None,
        subject_type: PartySubjectType | str = None,
        subject_id: int | None = None,
        display_name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        if app_name is None:
            raise ValueError("app_name is required")
        self.app_name = app_name if isinstance(app_name, PartyAppName) else PartyAppName(str(app_name))

        if subject_type is None:
            raise ValueError("subject_type is required")
        self.subject_type = (
            subject_type if isinstance(subject_type, PartySubjectType)
            else PartySubjectType(str(subject_type))
        )

        if subject_id is None or int(subject_id) <= 0:
            raise ValueError("subject_id must be a positive integer")

        self.id = id
        self.subject_id = int(subject_id)
        self.display_name = (str(display_name).strip() if display_name else None)
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "app_name": self.app_name.value,
            "subject_type": self.subject_type.value,
            "subject_id": self.subject_id,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
