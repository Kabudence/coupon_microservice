from peewee import (
    Model, ForeignKeyField, BigIntegerField, CompositeKey
)

from coupons.coupon.infraestructure.model.coupon_model import CouponModel
from shared.infrastructure.database import db


class CouponProductModel(Model):
    coupon = ForeignKeyField(
        CouponModel,
        field=CouponModel.id,
        backref='coupon_products',
        on_delete='CASCADE',
        null=False,
        index=False  # <- clave para evitar el índice automático
    )
    product_id = BigIntegerField(null=False)

    class Meta:
        database = db
        table_name = 'coupon_product'
        primary_key = CompositeKey('coupon', 'product_id')
        indexes = (
            (('coupon',), False),
            (('product_id',), False),
        )

