from typing import List, Optional

from coupons.segmentation.domain.entities.segment import SegmentData, SegmentGender
from coupons.segmentation.infraestructure.repositories.segment_repository import SegmentRepository


class SegmentQueryService:
    def __init__(self, repo: SegmentRepository):
        self.repo = repo

    def get_by_id(self, id_: int) -> Optional[SegmentData]:
        return self.repo.get_by_id(id_)

    def list_all(self) -> List[SegmentData]:
        return self.repo.get_all()

    def find_by_filters(
        self,
        public_name: Optional[str] = None,
        gender: Optional[SegmentGender | str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        is_student: Optional[bool] = None,
        district_id: Optional[int] = None,
        socioeconomic_level: Optional[str] = None,
    ) -> List[SegmentData]:
        return self.repo.find_by_filters(
            public_name=public_name,
            gender=gender,
            min_age=min_age,
            max_age=max_age,
            is_student=is_student,
            district_id=district_id,
            socioeconomic_level=socioeconomic_level,
        )
