# coupons_container.py
# ---------- IMPORT ALL REPOSITORIES ----------
from coupons.coupon.application.command.coupon_command_service import CouponCommandService
from coupons.coupon.application.queries.coupon_query_service import CouponQueryService
from coupons.coupon.infraestructure.repositories.coupon_repository import CouponRepository
from coupons.coupon_segment_price.application.command.coupon_segment_price_command_service import CouponSegmentPriceCommandService
from coupons.coupon_segment_price.application.queries.coupon_segment_price_query_service import CouponSegmentPriceQueryService
from coupons.coupon_segment_price.infraestructure.repositories.coupon_segment_price_repository import CouponSegmentPriceRepository
from coupons.coupon_trigger_product.application.command.coupon_trigger_product_command_service import CouponTriggerProductCommandService
from coupons.coupon_trigger_product.application.queries.coupon_trigger_product_query_service import CouponTriggerProductQueryService
from coupons.coupon_trigger_product.infraestructure.repositories.coupon_trigger_product_repository import CouponTriggerProductRepository
from coupons.coupons_type.application.command.coupon_type_command_service import CouponTypeCommandService
from coupons.coupons_type.application.queries.coupon_type_query_service import CouponTypeQueryService
from coupons.coupons_type.infraestructure.repositories.coupon_type_repository import CouponTypeRepository
from coupons.discount_type.application.command.discount_type_command_service import DiscountTypeCommandService
from coupons.discount_type.application.queries.discount_type_query_service import DiscountTypeQueryService
from coupons.discount_type.infraestructure.repositories.discount_type_repository import DiscountTypeRepository
from coupons.product_coupon.application.command.coupon_product_command_service import CouponProductCommandService
from coupons.product_coupon.application.queries.coupon_product_query_service import CouponProductQueryService
from coupons.product_coupon.infraestructure.repositories.coupon_product_repository import CouponProductRepository
from coupons.segmentation.application.command.segment_command_service import SegmentCommandService
from coupons.segmentation.application.queries.segment_query_service import SegmentQueryService
from coupons.segmentation.infraestructure.repositories.segment_repository import SegmentRepository


def build_coupon_services():
    # ---------- REPOSITORY INSTANTIATION ----------
    discount_type_repo = DiscountTypeRepository()
    coupon_type_repo = CouponTypeRepository()
    coupon_repo = CouponRepository()
    coupon_product_repo = CouponProductRepository()
    coupon_trigger_product_repo = CouponTriggerProductRepository()
    segment_repo = SegmentRepository()
    coupon_segment_price_repo = CouponSegmentPriceRepository()


    # ---------- SERVICE INSTANTIATION ----------
    # DiscountType
    discount_type_command_service = DiscountTypeCommandService(discount_type_repo)
    discount_type_query_service = DiscountTypeQueryService(discount_type_repo)

    # CouponType
    coupon_type_command_service = CouponTypeCommandService(coupon_type_repo)
    coupon_type_query_service = CouponTypeQueryService(coupon_type_repo)

    # Coupon (core)
    coupon_command_service = CouponCommandService(coupon_repo)
    coupon_query_service = CouponQueryService(coupon_repo)

    # CouponProduct
    coupon_product_command_service = CouponProductCommandService(coupon_product_repo)
    coupon_product_query_service = CouponProductQueryService(coupon_product_repo)

    # CouponTriggerProduct
    coupon_trigger_product_command_service = CouponTriggerProductCommandService(coupon_trigger_product_repo)
    coupon_trigger_product_query_service = CouponTriggerProductQueryService(coupon_trigger_product_repo)

    # Segment
    segment_command_service = SegmentCommandService(segment_repo)
    segment_query_service = SegmentQueryService(segment_repo)

    # CouponSegmentPrice
    coupon_segment_price_command_service = CouponSegmentPriceCommandService(coupon_segment_price_repo)
    coupon_segment_price_query_service = CouponSegmentPriceQueryService(coupon_segment_price_repo)



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



        # Repositories (exposed if you need them directly)
        "discount_type_repo": discount_type_repo,
        "coupon_type_repo": coupon_type_repo,
        "coupon_repo": coupon_repo,
        "coupon_product_repo": coupon_product_repo,
        "coupon_trigger_product_repo": coupon_trigger_product_repo,
        "segment_repo": segment_repo,
        "coupon_segment_price_repo": coupon_segment_price_repo,

    }
