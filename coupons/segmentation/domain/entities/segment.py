from typing import Optional
from enum import Enum


class SegmentGender(Enum):
    ANY = "ANY"
    M = "M"
    F = "F"
    X = "X"


class SegmentData:
    def __init__(
        self,
        id: int = None,
        public_name: str = "",
        gender: SegmentGender | str = SegmentGender.ANY,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        is_student: Optional[bool] = None,
        district_id: Optional[int] = None,
        socioeconomic_level: Optional[str] = None,
        created_at=None,
    ):
        if public_name is None or str(public_name).strip() == "":
            raise ValueError("public_name cannot be None or empty")

        self.id = id
        self.public_name = str(public_name).strip()

        self.gender = gender if isinstance(gender, SegmentGender) else SegmentGender(str(gender))

        if min_age is not None and min_age < 0:
            raise ValueError("min_age must be >= 0")
        if max_age is not None and max_age < 0:
            raise ValueError("max_age must be >= 0")
        if min_age is not None and max_age is not None and max_age < min_age:
            raise ValueError("max_age must be >= min_age")

        self.min_age = min_age
        self.max_age = max_age
        self.is_student = is_student
        self.district_id = district_id
        self.socioeconomic_level = (str(socioeconomic_level).strip() if socioeconomic_level else None)
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "public_name": self.public_name,
            "gender": self.gender.value if isinstance(self.gender, SegmentGender) else self.gender,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "is_student": self.is_student,
            "district_id": self.district_id,
            "socioeconomic_level": self.socioeconomic_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
