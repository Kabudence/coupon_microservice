# app.py
import os
from flask import Flask
from flask_cors import CORS

from coupons.alianza.interface.alianza_api import alianza_bp
from coupons.category.interface.category_api import category_bp
from coupons.coupon.interface.coupon_routes import coupon_bp
from coupons.coupon_trigger_product.interface.coupon_trigger_product_routes import coupon_trigger_product_bp
from coupons.coupons_type.interface.coupon_type_routes import coupon_type_bp
from coupons.event.interface.event_api import event_bp
from coupons.product_coupon.interface.coupon_product_routes import coupon_product_bp
from coupons.discount_type.interface.discount_type_routes import discount_type_bp  # <-- IMPORTANTE
from shared.factory.container_factory import build_coupon_services
from shared.infrastructure.database import init_db


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")

    # CORS para todo /api/*
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 🔹 Inicializa DB y servicios **al crear la app** (no esperes al primer request)
    init_db()
    coupon_services = build_coupon_services()
    app.config["coupon_services"] = coupon_services
    app.config["alianza_services"] = (
        coupon_services["alianza_command_service"],
        coupon_services["alianza_query_service"],

    )

    # Blueprints expuestos
    app.register_blueprint(coupon_type_bp)                 # /api/coupon-types
    app.register_blueprint(discount_type_bp)               # /api/discount-types  ✅ ahora sí
    app.register_blueprint(coupon_bp)                      # /api/coupons
    app.register_blueprint(coupon_product_bp)              # /api/coupon-products
    app.register_blueprint(coupon_trigger_product_bp)      # /api/coupon-trigger-products
    app.register_blueprint(alianza_bp)                     # /api/alliances (si aplica)
    app.register_blueprint(category_bp)                    # /api/coupon-categories
    app.register_blueprint(event_bp)                       # /api/coupon-events

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
