# app.py
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# ==== Blueprints (Cupones) ====
from coupons.alianza.interface.alianza_api import alianza_bp
from coupons.category.interface.category_api import category_bp
from coupons.coupon.interface.coupon_routes import coupon_bp
from coupons.coupon_trigger_product.interface.coupon_trigger_product_routes import coupon_trigger_product_bp
from coupons.coupons_client.interface.coupon_client_routes import coupon_client_bp
from coupons.coupons_type.interface.coupon_type_routes import coupon_type_bp
from coupons.event.interface.event_api import event_bp
from coupons.product_coupon.interface.coupon_product_routes import coupon_product_bp
from coupons.discount_type.interface.discount_type_routes import discount_type_bp

# ==== Blueprints (Pagos) ====
from payment.webhook.interface.flask_webhook_controller import create_mp_webhook_blueprint
from payment.checkout.interface.flask_checkout_session_controller import create_checkout_session_blueprint
from payment.orders.interface.order_controller import create_order_blueprint
from payment.party.interface.party_controller import create_party_blueprint
from payment.provider.provider_customer.interface.provider_customer_controller import create_provider_customer_blueprint
from payment.provider.provider_account.interface.provider_account_controller import create_provider_account_blueprint
from payment.provider.customer_sources.interface.customer_source_controller import create_payment_source_blueprint
from payment.provider.provider_account.interface.mp_oauth_controller import create_mp_oauth_blueprint

# Infraestructura
from shared.factory.container_factory import build_coupon_services
from shared.infrastructure.database import init_db


def create_app() -> Flask:
    app = Flask(__name__)
    load_dotenv()
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")

    # Config necesaria para OAuth PKCE
    app.config.update(
        MP_CLIENT_ID_TEST=os.getenv("MP_CLIENT_ID_TEST"),
        MP_CLIENT_ID_PROD=os.getenv("MP_CLIENT_ID_PROD") or os.getenv("MP_CLIENT_ID_TEST"),

        MP_REDIRECT_URI=os.getenv("MP_REDIRECT_URI"),

        MP_AUTH_BASE_URL=os.getenv("MP_AUTH_BASE_URL", "https://auth.mercadopago.com/authorization"),
        MP_TOKEN_URL=os.getenv("MP_TOKEN_URL", "https://api.mercadopago.com/oauth/token"),
        MP_API_BASE_URL=os.getenv("MP_API_BASE_URL", "https://api.mercadopago.com"),

        MP_PUBLIC_KEY_TEST=os.getenv("MP_PUBLIC_KEY_TEST"),
    )

    # CORS solo para endpoints /api/*
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── DB y servicios
    init_db()
    coupon_services = build_coupon_services()
    app.config["coupon_services"] = coupon_services
    app.config["services"] = coupon_services

    # ── Blueprints: Cupones
    app.register_blueprint(coupon_type_bp, url_prefix="/api/coupon-types")
    app.register_blueprint(discount_type_bp, url_prefix="/api/discount-types")
    app.register_blueprint(coupon_bp, url_prefix="/api/coupons")
    app.register_blueprint(coupon_product_bp, url_prefix="/api/coupon-products")
    app.register_blueprint(coupon_trigger_product_bp)
    app.register_blueprint(coupon_client_bp)
    app.register_blueprint(alianza_bp, url_prefix="/api/alliances")
    app.register_blueprint(category_bp, url_prefix="/api/coupon-categories")
    app.register_blueprint(event_bp, url_prefix="/api/coupon-events")

    # ── Blueprints: Pagos
    payments_base = "/api/payments"

    webhook_bp = create_mp_webhook_blueprint(url_prefix=f"{payments_base}/webhooks")
    app.register_blueprint(webhook_bp, url_prefix=webhook_bp.url_prefix)

    mp_oauth_bp = create_mp_oauth_blueprint()
    app.register_blueprint(mp_oauth_bp, url_prefix=f"{payments_base}/mp-oauth")

    checkout_session_bp = create_checkout_session_blueprint(url_prefix=f"{payments_base}/checkout-sessions")
    app.register_blueprint(checkout_session_bp, url_prefix=checkout_session_bp.url_prefix)

    orders_bp = create_order_blueprint(url_prefix=f"{payments_base}/orders")
    app.register_blueprint(orders_bp, url_prefix=orders_bp.url_prefix)

    parties_bp = create_party_blueprint(url_prefix=f"{payments_base}/parties")
    app.register_blueprint(parties_bp, url_prefix=parties_bp.url_prefix)

    provider_customers_bp = create_provider_customer_blueprint(url_prefix=f"{payments_base}/provider-customers")
    app.register_blueprint(provider_customers_bp, url_prefix=provider_customers_bp.url_prefix)

    provider_accounts_bp = create_provider_account_blueprint(url_prefix=f"{payments_base}/provider-accounts")
    app.register_blueprint(provider_accounts_bp, url_prefix=provider_accounts_bp.url_prefix)

    payment_sources_bp = create_payment_source_blueprint(url_prefix=f"{payments_base}/payment-sources")
    app.register_blueprint(payment_sources_bp, url_prefix=payment_sources_bp.url_prefix)

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
