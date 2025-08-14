import datetime
from peewee import (
    Model, AutoField, CharField, IntegerField, BooleanField, BigIntegerField,
    DateTimeField, Index
)

from coupons.segmentation.domain.entities.segment import SegmentGender
from shared.infrastructure.database import db


class SegmentModel(Model):
    id = AutoField(primary_key=True)

    # nombre_publico
    public_name = CharField(max_length=80, null=False, column_name="nombre_publico")

    # genero
    gender = CharField(
        max_length=8,
        null=False,
        default=SegmentGender.ANY.value,
        choices=[(g.value, g.value) for g in SegmentGender],
        column_name="genero"
    )

    # edad_min / edad_max
    min_age = IntegerField(null=True, column_name="edad_min")
    max_age = IntegerField(null=True, column_name="edad_max")

    # es_estudiante
    is_student = BooleanField(null=True, column_name="es_estudiante")

    # distrito_id (nullable)
    district_id = BigIntegerField(null=True, column_name="distrito_id")

    # nivel_socioeconomico (nullable)
    socioeconomic_level = CharField(max_length=50, null=True, column_name="nivel_socioeconomico")

    # creado_en
    created_at = DateTimeField(default=datetime.datetime.now, null=False, column_name="creado_en")

    class Meta:
        database = db
        table_name = "segmento"
        indexes = (
            # idx_seg_base (genero, edad_min, edad_max)
            (("gender", "min_age", "max_age"), False),
            # idx_seg_distrito
            (("district_id",), False),
            # idx_seg_nivel
            (("socioeconomic_level",), False),
        )
