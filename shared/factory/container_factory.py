# coupons_container.py

# ---------- IMPORT ALL REPOSITORIES / SERVICES ----------
from coupons.alianza.application.command.alianza_commands import AlianzaCommandService
from coupons.alianza.application.queries.alianza_queries import AlianzaQueryService
from coupons.alianza.infraestructure.repositories.alianza_repository import AlianzaRepository

from coupons.category.application.command.category_command_service import CategoryCommandService
from coupons.category.application.queries.category_query_service import CategoryQueryService
from coupons.category.infraestructure.repositories.category_repository import CategoryRepository

from coupons.coupon.application.command.coupon_command_service import CouponCommandService
from coupons.coupon.application.queries.coupon_query_service import CouponQueryService
from coupons.coupon.infraestructure.repositories.coupon_repository import CouponRepository

from coupons.coupon_segment_price.application.command.coupon_segment_price_command_service import CouponSegmentPriceCommandService
from coupons.coupon_segment_price.application.queries.coupon_segment_price_query_service import CouponSegmentPriceQueryService
from coupons.coupon_segment_price.infraestructure.repositories.coupon_segment_price_repository import CouponSegmentPriceRepository

from coupons.coupon_trigger_product.application.command.coupon_trigger_product_command_service import CouponTriggerProductCommandService
from coupons.coupon_trigger_product.application.queries.coupon_trigger_product_query_service import CouponTriggerProductQueryService
from coupons.coupon_trigger_product.infraestructure.repositories.coupon_trigger_product_repository import CouponTriggerProductRepository
from coupons.coupons_client.application.command.coupon_client_command_service import CouponClientCommandService
from coupons.coupons_client.application.queries.coupon_client_query_service import CouponClientQueryService
from coupons.coupons_client.infraestructure.repositories.coupon_client_repository import CouponClientRepository

from coupons.coupons_type.application.command.coupon_type_command_service import CouponTypeCommandService
from coupons.coupons_type.application.queries.coupon_type_query_service import CouponTypeQueryService
from coupons.coupons_type.infraestructure.repositories.coupon_type_repository import CouponTypeRepository

from coupons.discount_type.application.command.discount_type_command_service import DiscountTypeCommandService
from coupons.discount_type.application.queries.discount_type_query_service import DiscountTypeQueryService
from coupons.discount_type.infraestructure.repositories.discount_type_repository import DiscountTypeRepository

from coupons.event.application.command.event_command_service import EventCommandService
from coupons.event.application.queries.event_query_service import EventQueryService
from coupons.event.infraestructure.repositories.event_repository import EventRepository

# ---- PRODUCT COUPON (mapping cupón ↔ producto/servicio) ----
from coupons.product_coupon.application.command.coupon_product_command_service import CouponProductCommandService
from coupons.product_coupon.application.queries.coupon_product_query_service import CouponProductQueryService
from coupons.product_coupon.infraestructure.repositories.coupon_product_repository import CouponProductRepository
from coupons.segmentation.application.command.segment_command_service import SegmentCommandService
from coupons.segmentation.application.queries.segment_query_service import SegmentQueryService
from coupons.segmentation.infraestructure.repositories.segment_repository import SegmentRepository
from payment.checkout.application.command.checkout_session_command_service import CheckoutSessionCommandService
from payment.checkout.application.queries.checkout_session_query_service import CheckoutSessionQueryService
from payment.checkout.infraestructure.repositories.checkout_session_repository import CheckoutSessionRepository
from payment.orders.application.command.order_command_service import OrderCommandService
from payment.orders.application.queries.order_query_service import OrderQueryService
from payment.orders.infraestructure.repositories.order_repository import OrderRepository
from payment.party.application.command.party_command_service import PartyCommandService
from payment.party.application.queries.party_query_service import PartyQueryService
from payment.party.infraestructure.repositories.party_repository import PartyRepository
from payment.provider.customer_sources.application.command.payment_source_command_service import \
    PaymentSourceCommandService
from payment.provider.customer_sources.infraestructure.repositories.payment_source_repository import \
    PaymentSourceRepository
from payment.provider.provider_account.application.command.provider_account_command_service import \
    ProviderAccountCommandService
from payment.provider.provider_account.application.queries.provider_account_query_service import \
    ProviderAccountQueryService
from payment.provider.provider_account.infraestructure.repositories.provider_account_repository import \
    ProviderAccountRepository
from payment.provider.provider_customer.application.command.provider_customer_command_service import \
    ProviderCustomerCommandService
from payment.provider.provider_customer.infraestructure.repositories.provider_customer_repository import \
    ProviderCustomerRepository
from payment.webhook.application.command.webhook_event_command_service import WebhookEventCommandService
from payment.webhook.application.queries.webhook_event_query_service import WebhookEventQueryService
from payment.webhook.infraestructure.repositories.webhook_event_repository import WebhookEventRepository


def build_coupon_services():
    # ---------- REPOSITORIES ----------
    discount_type_repo = DiscountTypeRepository()
    coupon_type_repo = CouponTypeRepository()
    coupon_repo = CouponRepository()

    coupon_product_repo = CouponProductRepository()
    coupon_trigger_product_repo = CouponTriggerProductRepository()

    segment_repo = SegmentRepository()
    coupon_segment_price_repo = CouponSegmentPriceRepository()

    category_repo = CategoryRepository()
    event_repo = EventRepository()

    alianza_repo = AlianzaRepository()





    webhook_repo= WebhookEventRepository()
    webhook_command_service = WebhookEventCommandService(webhook_repo)
    webhook_query_service = WebhookEventQueryService(webhook_repo)
    checkout_session_repo =  CheckoutSessionRepository()
    checkout_session_command_service = CheckoutSessionCommandService(checkout_session_repo)
    checkout_session_query_service = CheckoutSessionQueryService(checkout_session_repo)
    orders_repo = OrderRepository()
    order_query_service = OrderQueryService(orders_repo)
    order_command_service = OrderCommandService(orders_repo)
    party_repository = PartyRepository()
    party_query_service = PartyQueryService(party_repository)
    party_command_service =PartyCommandService(party_repository)
    payment_source_repo = PaymentSourceRepository()
    payment_source_command_service = PaymentSourceCommandService(payment_source_repo)
    payment_source_query_service = PaymentSourceCommandService(payment_source_repo)
    provider_account_repository = ProviderAccountRepository()
    provider_account_command_service = ProviderAccountCommandService(provider_account_repository)
    provider_account_query_service = ProviderAccountQueryService(provider_account_repository)
    provider_customer_repo =ProviderCustomerRepository()
    provider_customer_command_service = ProviderCustomerCommandService(provider_customer_repo)
    provider_customer_query_service = ProviderCustomerCommandService(provider_customer_repo)
    # ---------- SERVICES ----------
    # Catálogos
    discount_type_command_service = DiscountTypeCommandService(discount_type_repo)
    discount_type_query_service = DiscountTypeQueryService(discount_type_repo)

    coupon_type_command_service = CouponTypeCommandService(coupon_type_repo)
    coupon_type_query_service = CouponTypeQueryService(coupon_type_repo)

    # Coupon (core)
    coupon_command_service = CouponCommandService(coupon_repo)
    coupon_query_service = CouponQueryService(coupon_repo)

    # CouponProduct (mapping). Incluye métodos nuevos: consume_one / remove_by_combo (ya en el service/repo)
    coupon_product_command_service = CouponProductCommandService(coupon_product_repo)
    coupon_product_query_service = CouponProductQueryService(coupon_product_repo)

    # CouponTriggerProduct (triggers que generan cupones)
    coupon_trigger_product_command_service = CouponTriggerProductCommandService(coupon_trigger_product_repo)
    coupon_trigger_product_query_service = CouponTriggerProductQueryService(coupon_trigger_product_repo)

    # Segmentación / precios por segmento
    segment_command_service = SegmentCommandService(segment_repo)
    segment_query_service = SegmentQueryService(segment_repo)

    coupon_segment_price_command_service = CouponSegmentPriceCommandService(coupon_segment_price_repo)
    coupon_segment_price_query_service = CouponSegmentPriceQueryService(coupon_segment_price_repo)

    # Category / Event
    category_command_service = CategoryCommandService(category_repo)
    category_query_service = CategoryQueryService(category_repo)

    event_command_service = EventCommandService(event_repo)
    event_query_service = EventQueryService(event_repo)

    # Alianzas
    alianza_command_service = AlianzaCommandService(alianza_repo)
    alianza_query_service = AlianzaQueryService(alianza_repo)

    # CouponClient (cupones emitidos/personalizados por cliente)
    coupon_client_repo = CouponClientRepository()
    coupon_client_command_service = CouponClientCommandService(coupon_client_repo)
    coupon_client_query_service = CouponClientQueryService(coupon_client_repo)

    # ---------- RETURN MAP ----------
    return {
        # Catalogs
        "discount_type_command_service": discount_type_command_service,
        "discount_type_query_service": discount_type_query_service,
        "coupon_type_command_service": coupon_type_command_service,
        "coupon_type_query_service": coupon_type_query_service,

        # Coupon core
        "coupon_command_service": coupon_command_service,
        "coupon_query_service": coupon_query_service,

        # Relations / mappings
        "coupon_product_command_service": coupon_product_command_service,
        "coupon_product_query_service": coupon_product_query_service,

        "coupon_trigger_product_command_service": coupon_trigger_product_command_service,
        "coupon_trigger_product_query_service": coupon_trigger_product_query_service,

        # Segmentation
        "segment_command_service": segment_command_service,
        "segment_query_service": segment_query_service,
        "coupon_segment_price_command_service": coupon_segment_price_command_service,
        "coupon_segment_price_query_service": coupon_segment_price_query_service,

        # Category / Event
        "category_command_service": category_command_service,
        "category_query_service": category_query_service,
        "event_command_service": event_command_service,
        "event_query_service": event_query_service,

        # Alliances
        "alianza_command_service": alianza_command_service,
        "alianza_query_service": alianza_query_service,

        # ---- coupon_client (nuevo) ----
        "coupon_client_command_service": coupon_client_command_service,
        "coupon_client_query_service": coupon_client_query_service,

        # (Opcional) Exponer repos si los necesitas
        "discount_type_repo": discount_type_repo,
        "coupon_type_repo": coupon_type_repo,
        "coupon_repo": coupon_repo,
        "coupon_product_repo": coupon_product_repo,
        "coupon_trigger_product_repo": coupon_trigger_product_repo,
        "segment_repo": segment_repo,
        "coupon_segment_price_repo": coupon_segment_price_repo,
        "category_repo": category_repo,
        "event_repo": event_repo,
        "alianza_repo": alianza_repo,
        "coupon_client_repo": coupon_client_repo,





        "webhook_command_service": webhook_command_service,
        "webhook_query_service": webhook_query_service,
        "checkout_session_command_service": checkout_session_command_service,
        "checkout_session_query_service": checkout_session_query_service,
        "order_command_service": order_command_service,
        "order_query_service": order_query_service,
        "party_command_service": party_command_service,
        "party_query_service": party_query_service,
        "payment_source_command_service": payment_source_command_service,
        "payment_source_query_service": payment_source_query_service,
        "provider_account_command_service": provider_account_command_service,
        "provider_account_query_service": provider_account_query_service,
        "provider_customer_command_service": provider_customer_command_service,
        "provider_customer_query_service": provider_customer_query_service,
    }
