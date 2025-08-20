"""
Database connection + table-creation helpers.
¡¡NO IMPORTES modelos ARRIBA!!  Eso crea ciclos.
"""

from peewee import MySQLDatabase, SQL  # SQL para constraints / expresiones crudas

from shared.infrastructure.db_config import DB_CONFIG



# ------------- conexión -------------
db = MySQLDatabase(**DB_CONFIG)

# Peewee expone peewee.SQL; algunos modelos podrían usar db.SQL(…).
# Añadimos el alias para no tocar cada modelo.
if not hasattr(db, "SQL"):
    db.SQL = SQL


# ------------------------------------------------------------------
# Función para crear TODAS las tablas.  Importa modelos **dentro**.
# ------------------------------------------------------------------
def init_db() -> None:
    """
    Conecta (si está cerrada) y crea TODAS las tablas definidas en los modelos
    de la capa 'infrastructure.model' de coupons/segments.
    Ejecuta con:  from shared.infrastructure.database import init_db; init_db()
    """
    if db.is_closed():
        db.connect(reuse_if_open=True)
        print("Driver conectado:", type(db._state.conn))

    # ------------ IMPORTS LOCALES (evitar ciclos) ------------
    from coupons.coupon.infraestructure.model.coupon_model import CouponModel
    from coupons.coupon_segment_price.infraestructure.model.coupon_segment_price_model import CouponSegmentPriceModel
    from coupons.coupon_trigger_product.infraestructure.model.coupon_trigger_product_model import CouponTriggerProductModel
    from coupons.coupons_type.infraestructure.model.coupon_type_model import CouponTypeModel
    from coupons.discount_type.infraestructure.model.discount_type_model import DiscountTypeModel
    from coupons.product_coupon.infraestructure.model.coupon_product_model import CouponProductModel
    from coupons.segmentation.infraestructure.model.segment_model import SegmentModel
    from coupons.alianza.infraestructure.model.alianza_model import AlianzaModel
    from coupons.category.infraestructure.model.category_model import CategoryModel
    from coupons.event.infraestructure.model.event_model import EventModel
    from coupons.coupons_client.infraestructure.model.coupon_client_model import CouponClientModel

    # ------------ CREAR TABLAS ---------------
    db.create_tables(
        [
            # Catalogs
            DiscountTypeModel,
            CouponTypeModel,

            # Core
            CouponModel,

            # Relations
            CouponProductModel,
            CouponTriggerProductModel,

            # Segmentation
            SegmentModel,
            CouponSegmentPriceModel,
            AlianzaModel,
            CategoryModel,
            EventModel,
            CouponClientModel,
        ],
        safe=True,
    )

    print("✅ Tablas creadas/aseguradas.")
    db.close()
