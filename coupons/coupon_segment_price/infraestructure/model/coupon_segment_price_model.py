from peewee import (
    Model, ForeignKeyField, DecimalField, IntegerField, CompositeKey
)

from coupons.coupon.infraestructure.model.coupon_model import CouponModel
from coupons.discount_type.infraestructure.model.discount_type_model import DiscountTypeModel
from coupons.segmentation.infraestructure.model.segment_model import SegmentModel
from shared.infrastructure.database import db



class CouponSegmentPriceModel(Model):
    coupon = ForeignKeyField(
        CouponModel,
        field=CouponModel.id,
        backref='segment_prices',
        on_delete='CASCADE',
        null=False,
        column_name='cupon_id'
    )
    segment = ForeignKeyField(
        SegmentModel,
        field=SegmentModel.id,
        backref='coupon_prices',
        on_delete='CASCADE',
        null=False,
        column_name='segmento_id'
    )
    discount_type = ForeignKeyField(
        DiscountTypeModel,
        field=DiscountTypeModel.id,
        backref='coupon_segment_prices',
        null=False,
        column_name='tipo_descuento_id'
    )
    value = DecimalField(max_digits=12, decimal_places=2, auto_round=True, null=False, column_name='valor')
    priority = IntegerField(null=False, default=1, column_name='prioridad')

    class Meta:
        database = db
        table_name = 'cupon_segmento_precio'
        primary_key = CompositeKey('coupon', 'segment')
        indexes = (
            (('coupon', 'priority'), False),  # idx_csp_prio
        )
