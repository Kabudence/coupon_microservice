from peewee import Model, AutoField, CharField

from coupons.discount_type.domain.entities.discount_type import DiscountTypeName
from shared.infrastructure.database import db


class DiscountTypeModel(Model):
    id = AutoField(primary_key=True)
    name = CharField(
        max_length=20,
        unique=True,
        null=False,
        choices=[(e.value, e.value) for e in DiscountTypeName]
    )

    class Meta:
        database = db
        table_name = 'discount_type'
