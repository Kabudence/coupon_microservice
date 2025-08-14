from typing import Optional, List

from coupons.segmentation.domain.entities.segment import SegmentData, SegmentGender
from coupons.segmentation.infraestructure.model.segment_model import SegmentModel


class SegmentRepository:
    def _to_entity(self, rec: SegmentModel) -> SegmentData:
        return SegmentData(
            id=rec.id,
            public_name=rec.public_name,
            gender=SegmentGender(rec.gender),
            min_age=rec.min_age,
            max_age=rec.max_age,
            is_student=rec.is_student,
            district_id=rec.district_id,
            socioeconomic_level=rec.socioeconomic_level,
            created_at=rec.created_at,
        )

    def get_by_id(self, id_: int) -> Optional[SegmentData]:
        try:
            rec = SegmentModel.get(SegmentModel.id == id_)
            return self._to_entity(rec)
        except SegmentModel.DoesNotExist:
            return None

    def get_all(self) -> List[SegmentData]:
        return [self._to_entity(rec) for rec in SegmentModel.select()]

    def create(self, segment: SegmentData) -> SegmentData:
        rec = SegmentModel.create(
            public_name=segment.public_name,
            gender=(segment.gender.value if isinstance(segment.gender, SegmentGender) else str(segment.gender)),
            min_age=segment.min_age,
            max_age=segment.max_age,
            is_student=segment.is_student,
            district_id=segment.district_id,
            socioeconomic_level=segment.socioeconomic_level,
        )
        return self._to_entity(rec)

    def update(self, segment: SegmentData) -> Optional[SegmentData]:
        try:
            rec = SegmentModel.get(SegmentModel.id == segment.id)
            rec.public_name = segment.public_name
            rec.gender = (segment.gender.value if isinstance(segment.gender, SegmentGender) else str(segment.gender))
            rec.min_age = segment.min_age
            rec.max_age = segment.max_age
            rec.is_student = segment.is_student
            rec.district_id = segment.district_id
            rec.socioeconomic_level = segment.socioeconomic_level
            rec.save()
            return self._to_entity(rec)
        except SegmentModel.DoesNotExist:
            return None

    def delete(self, id_: int) -> bool:
        try:
            rec = SegmentModel.get(SegmentModel.id == id_)
            rec.delete_instance()
            return True
        except SegmentModel.DoesNotExist:
            return False

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
        q = SegmentModel.select()
        if public_name:
            q = q.where(SegmentModel.public_name == public_name.strip())
        if gender:
            gv = gender.value if isinstance(gender, SegmentGender) else str(gender)
            q = q.where(SegmentModel.gender == gv)
        if min_age is not None:
            q = q.where((SegmentModel.min_age.is_null(True)) | (SegmentModel.min_age >= min_age))
        if max_age is not None:
            q = q.where((SegmentModel.max_age.is_null(True)) | (SegmentModel.max_age <= max_age))
        if is_student is not None:
            q = q.where(SegmentModel.is_student == is_student)
        if district_id is not None:
            q = q.where(SegmentModel.district_id == district_id)
        if socioeconomic_level:
            q = q.where(SegmentModel.socioeconomic_level == socioeconomic_level.strip())
        return [self._to_entity(rec) for rec in q]
