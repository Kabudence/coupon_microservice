from peewee import (
    Model, ForeignKeyField, BigIntegerField, CompositeKey, CharField, IntegerField
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
        index=False
    )
    product_id = BigIntegerField(null=False)

    code = CharField(max_length=100, null=False)
    product_type = CharField(max_length=16, null=False, choices=[("PRODUCT", "PRODUCT"), ("SERVICE", "SERVICE")])

    # NUEVOS
    stock = IntegerField(null=True)  # >=0, opcional
    status = CharField(max_length=16, null=False, default="ACTIVE", choices=[("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE")])

    class Meta:
        database = db
        table_name = 'coupon_product'
        primary_key = CompositeKey('coupon', 'product_id')
        indexes = (
            (('coupon',), False),
            (('product_id',), False),
            (('code',), False),
            (('product_type',), False),
            (('status',), False),
        )
