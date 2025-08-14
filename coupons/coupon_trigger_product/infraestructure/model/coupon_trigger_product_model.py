from peewee import (
    Model, ForeignKeyField, BigIntegerField, IntegerField, DecimalField,
    CompositeKey
)

from coupons.coupon.infraestructure.model.coupon_model import CouponModel
from shared.infrastructure.database import db


class CouponTriggerProductModel(Model):
    # If you have ProductModel, change to ForeignKeyField(ProductModel, ...)
    product_trigger_id = BigIntegerField(null=False)

    coupon = ForeignKeyField(
        CouponModel,
        field=CouponModel.id,
        backref='trigger_products',
        on_delete='CASCADE',
        null=False
    )

    min_quantity = IntegerField(null=False, default=1)
    min_amount   = DecimalField(max_digits=12, decimal_places=2, auto_round=True, null=True)

    class Meta:
        database = db
        table_name = 'coupon_trigger_product'
        primary_key = CompositeKey('product_trigger_id', 'coupon')
        indexes = (
            (('coupon',), False),                # idx_ctp_coupon
            (('product_trigger_id',), False),    # idx_ctp_product_trigger
        )
