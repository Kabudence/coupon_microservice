from typing import Optional

from coupons.segmentation.domain.entities.segment import SegmentGender, SegmentData
from coupons.segmentation.infraestructure.repositories.segment_repository import SegmentRepository


class SegmentCommandService:
    def __init__(self, repo: SegmentRepository):
        self.repo = repo

    def create(
        self,
        public_name: str,
        gender: SegmentGender | str = SegmentGender.ANY,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        is_student: Optional[bool] = None,
        district_id: Optional[int] = None,
        socioeconomic_level: Optional[str] = None,
    ) -> SegmentData:
        entity = SegmentData(
            public_name=public_name,
            gender=gender,
            min_age=min_age,
            max_age=max_age,
            is_student=is_student,
            district_id=district_id,
            socioeconomic_level=socioeconomic_level,
        )
        return self.repo.create(entity)

    def update(
        self,
        id_: int,
        public_name: str,
        gender: SegmentGender | str = SegmentGender.ANY,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        is_student: Optional[bool] = None,
        district_id: Optional[int] = None,
        socioeconomic_level: Optional[str] = None,
    ) -> Optional[SegmentData]:
        current = self.repo.get_by_id(id_)
        if not current:
            raise ValueError("Segment not found.")

        current.public_name = public_name
        current.gender = gender if isinstance(gender, SegmentGender) else SegmentGender(str(gender))
        current.min_age = min_age
        current.max_age = max_age
        current.is_student = is_student
        current.district_id = district_id
        current.socioeconomic_level = socioeconomic_level

        return self.repo.update(current)

    def delete(self, id_: int) -> bool:
        return self.repo.delete(id_)
