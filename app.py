# app.py
import os
from flask import Flask

from coupons.coupon.interface.coupon_routes import coupon_bp
from coupons.coupon_trigger_product.interface.coupon_trigger_product_routes import coupon_trigger_product_bp
from coupons.coupons_type.interface.coupon_type_routes import coupon_type_bp
from coupons.product_coupon.interface.coupon_product_routes import coupon_product_bp
from shared.factory.container_factory import build_coupon_services

from shared.infrastructure.database import init_db




def create_app() -> Flask:
    app = Flask(__name__)
    # Use env var in production
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")

    # Register blueprints you want to expose
    app.register_blueprint(coupon_type_bp)
    app.register_blueprint(coupon_bp)
    app.register_blueprint(coupon_product_bp)
    app.register_blueprint(coupon_trigger_product_bp)

    # Optional healthcheck
    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    # One-time bootstrapping (DB + DI) on first request
    first_request = {"done": False}

    @app.before_request
    def bootstrap_once():
        if not first_request["done"]:
            first_request["done"] = True
            # 1) init DB schema/tables
            init_db()
            # 2) Build coupon services and inject them into config
            coupon_services = build_coupon_services()
            app.config["coupon_services"] = coupon_services

    return app


# Local run
if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", "5001")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
